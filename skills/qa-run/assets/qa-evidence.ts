import { expect, type Locator, type Page } from "@playwright/test";

/**
 * Helpers the `qa-run` skill's generated specs share. They hold what every pass needs and no pass-specific data.
 * Configure them through env vars (or edit the defaults below to match docs/qa-setup.md):
 * - QA_THEME: `light` for the light pass, dark otherwise.
 * - QA_THEME_STORAGE_KEY / QA_THEME_STORAGE_FIELD: the localStorage key (and JSON field) the app keeps its theme in.
 *   Unset: the theme is applied through `prefers-color-scheme` only.
 * - QA_API_ORIGIN: the API origin `apiCapture` calls.
 */

export type Theme = "light" | "dark";

/** The theme a pass runs in: `QA_THEME=light` for the light pass, dark otherwise. */
export function passTheme(): Theme {
  return process.env["QA_THEME"] === "light" ? "light" : "dark";
}

/** Applies `theme` before any page script runs: the media emulation, plus the app's stored setting when it has one. */
export async function applyTheme(page: Page, theme: Theme = passTheme()): Promise<void> {
  await page.emulateMedia({ colorScheme: theme });
  const key = process.env["QA_THEME_STORAGE_KEY"];
  if (!key) return;
  const field = process.env["QA_THEME_STORAGE_FIELD"];
  await page.addInitScript(
    ([storageKey, storageField, value]) => {
      try {
        if (!storageField) {
          localStorage.setItem(storageKey, value);
          return;
        }
        const settings = JSON.parse(localStorage.getItem(storageKey) ?? "{}") as Record<string, unknown>;
        localStorage.setItem(storageKey, JSON.stringify({ ...settings, [storageField]: value }));
      } catch {
        // A document without storage (about:blank, data:) keeps the app default.
      }
    },
    [key, field ?? "", theme] as const,
  );
}

export interface ContrastIssue {
  text: string;
  ratio: number;
  required: number;
  color: string;
  background: string;
}

/**
 * Visible text in `scope` whose contrast against its effective background falls below WCAG AA:
 * 4.5:1, or 3:1 for large text (24px, or 18.66px bold). Disabled controls are exempt, and text over an
 * image or a gradient is skipped because its background cannot be read from computed styles.
 */
export async function contrastIssues(scope: Page | Locator): Promise<ContrastIssue[]> {
  const root = "goto" in scope ? scope.locator(":root") : scope;
  return root.evaluate((start: Element) => {
    const parse = (value: string): [number, number, number, number] | null => {
      const m = value.match(/rgba?\(([^)]+)\)/);
      if (!m) return null;
      const parts = m[1]
        .split(/[\s,/]+/)
        .filter(Boolean)
        .map(Number);
      return [parts[0], parts[1], parts[2], parts.length > 3 ? parts[3] : 1];
    };
    const luminance = ([r, g, b]: number[]): number => {
      const channel = (c: number): number => {
        const s = c / 255;
        return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
      };
      return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
    };
    const background = (el: Element | null): [number, number, number] | null => {
      for (let node = el; node; node = node.parentElement) {
        const style = getComputedStyle(node);
        if (style.backgroundImage !== "none") return null;
        const bg = parse(style.backgroundColor);
        if (bg && bg[3] > 0.5) return [bg[0], bg[1], bg[2]];
      }
      return [255, 255, 255];
    };
    // Helpers stay inside this function: `evaluate` serializes only the function it runs in the page.
    const isRendered = (el: Element, style: CSSStyleDeclaration): boolean => {
      const rect = el.getBoundingClientRect();
      return !!rect.width && !!rect.height && style.visibility !== "hidden" && Number(style.opacity) !== 0;
    };
    const issueFor = (el: Element, text: string): ContrastIssue | null => {
      if (el.closest("[disabled], [aria-disabled='true'], [aria-hidden='true']")) return null;
      const style = getComputedStyle(el);
      if (!isRendered(el, style)) return null;
      const fg = parse(style.color);
      const bg = background(el);
      if (!fg || !bg) return null;
      const [light, dark] = [luminance(fg), luminance(bg)].sort((a, b) => b - a);
      const ratio = (light + 0.05) / (dark + 0.05);
      const size = parseFloat(style.fontSize);
      const large = size >= 24 || (size >= 18.66 && Number(style.fontWeight) >= 700);
      const required = large ? 3 : 4.5;
      if (ratio >= required) return null;
      return {
        text: text.slice(0, 60),
        ratio: Math.round(ratio * 100) / 100,
        required,
        color: style.color,
        background: `rgb(${bg.join(", ")})`,
      };
    };
    const issues: ContrastIssue[] = [];
    const seen = new Set<Element>();
    const walker = document.createTreeWalker(start, NodeFilter.SHOW_TEXT);
    for (let node = walker.nextNode(); node && issues.length < 50; node = walker.nextNode()) {
      const el = node.parentElement;
      const text = (node.textContent ?? "").trim();
      if (!el || !text || seen.has(el)) continue;
      seen.add(el);
      const issue = issueFor(el, text);
      if (issue) issues.push(issue);
    }
    return issues;
  });
}

/** Navigates inside the running app, without a document load, so session-scoped state such as a reveal survives. */
export async function spaNavigate(page: Page, url: string): Promise<void> {
  await page.evaluate(target => {
    history.pushState({}, "", target);
    dispatchEvent(new PopStateEvent("popstate", { state: {} }));
  }, url);
  await page.waitForURL(u => u.pathname + u.search === url);
}

export interface ApiCaller {
  /** The captured bearer header, empty until the app has called the API. */
  token: () => string;
  call: (method: "GET" | "POST", path: string, data?: unknown) => Promise<{ status: number; body: string }>;
}

/**
 * Calls the API with the bearer token the app itself sends. Only requests to `apiOrigin` are captured:
 * the first authorized request of a page is often an identity provider's, whose token the API rejects.
 */
export function apiCapture(page: Page, apiOrigin = process.env["QA_API_ORIGIN"] ?? "http://localhost:5000"): ApiCaller {
  let bearer = "";
  page.on("request", r => {
    const auth = r.headers()["authorization"];
    if (auth && !bearer && new URL(r.url()).origin === apiOrigin) bearer = auth;
  });
  return {
    token: () => bearer,
    call: async (method, path, data) => {
      await expect.poll(() => bearer, { message: "the app sent an authorized API request" }).not.toBe("");
      const r = await page.request.fetch(`${apiOrigin}${path}`, {
        method,
        headers: { authorization: bearer, "content-type": "application/json" },
        data,
      });
      return { status: r.status(), body: await r.text() };
    },
  };
}
