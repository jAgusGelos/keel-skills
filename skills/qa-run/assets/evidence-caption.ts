import { test, type Page } from "@playwright/test";

export const EVIDENCE_CAPTION_SELECTOR = "[data-qa-evidence-caption]";
const CAPTION_READING_TIME_MS = 1_000;

/**
 * Runs one Playwright evidence step while embedding its description in the recorded viewport.
 *
 * @param page - Browser page recorded by the evidence run.
 * @param description - Shared wording for the Playwright step, video caption, and storyboard row.
 * @param action - User-visible interaction or assertion demonstrated by the step.
 * @returns The value returned by the step action.
 */
export async function captionedStep<T>(page: Page, description: string, action: () => Promise<T>): Promise<T> {
  return test.step(description, async () => {
    await renderCaption(page, description);

    try {
      const result = await action();
      await renderCaptionForReading(page, description);
      return result;
    } catch (error: unknown) {
      await retainCaptionAfterFailure(page, description);
      throw error;
    }
  });
}

async function renderCaptionForReading(page: Page, description: string): Promise<void> {
  await renderCaption(page, description);
  await page.waitForTimeout(CAPTION_READING_TIME_MS);
}

async function retainCaptionAfterFailure(page: Page, description: string): Promise<void> {
  if (page.isClosed()) {
    return;
  }

  try {
    await renderCaptionForReading(page, description);
  } catch {
    // The action's original failure is the evidence result; caption cleanup must not replace it.
  }
}

async function renderCaption(page: Page, description: string): Promise<void> {
  await page.evaluate(
    ({ captionSelector, captionText }) => {
      const existingCaption = document.querySelector(captionSelector);
      let caption: HTMLElement;
      if (existingCaption instanceof HTMLElement) {
        caption = existingCaption;
      } else {
        caption = document.createElement("div");
        caption.setAttribute("data-qa-evidence-caption", "");
        caption.setAttribute("role", "status");
        caption.setAttribute("aria-live", "polite");
        caption.setAttribute("aria-atomic", "true");
        const parent = document.body ?? document.documentElement;
        if (!parent) {
          throw new Error("The evidence document has no caption host.");
        }
        parent.append(caption);
      }

      caption.textContent = captionText;
      Object.assign(caption.style, {
        backgroundColor: "CanvasText",
        border: "2px solid Canvas",
        borderRadius: "0.5rem",
        bottom: "1.5rem",
        color: "Canvas",
        font: "600 1.25rem/1.4 system-ui, sans-serif",
        left: "50%",
        maxWidth: "min(calc(100vw - 3rem), 60rem)",
        overflowWrap: "anywhere",
        padding: "0.75rem 1rem",
        pointerEvents: "none",
        position: "fixed",
        textAlign: "center",
        transform: "translateX(-50%)",
        whiteSpace: "normal",
        width: "max-content",
        zIndex: "2147483647",
      });
    },
    { captionSelector: EVIDENCE_CAPTION_SELECTOR, captionText: description },
  );
}
