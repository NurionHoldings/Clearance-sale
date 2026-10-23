import { test, expect } from '@playwright/test';

for (const viewport of [
  { name: 'small-mobile', width: 320, height: 640 },
  { name: 'iphone', width: 390, height: 844 },
  { name: 'android', width: 412, height: 915 },
  { name: 'landscape', width: 844, height: 390 },
  { name: 'desktop', width: 1440, height: 900 },
]) {
  test(`Asia Holdings logo layout: ${viewport.name}`, async ({ page }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    await page.goto('/asia-holdings-logo-demo.html');
    const skip = page.locator('#skipEntry');
    if (await skip.isVisible()) await skip.click();
    await expect(page.locator('.logo')).toBeVisible();
    await expect(page.locator('.logo')).toHaveJSProperty('naturalWidth', 700);
    const metrics = await page.evaluate(() => ({
      scroll: document.documentElement.scrollWidth,
      viewport: document.documentElement.clientWidth,
      stage: document.querySelector('.stage').getBoundingClientRect().toJSON(),
    }));
    expect(metrics.scroll).toBeLessThanOrEqual(metrics.viewport + 1);
    expect(metrics.stage.width).toBeLessThanOrEqual(viewport.width);
    for (const id of ['play', 'replay', 'level', 'intro']) {
      const button = page.locator('#' + id);
      await expect(button).toBeVisible();
      const box = await button.boundingBox();
      expect(box.width).toBeGreaterThanOrEqual(44);
      expect(box.height).toBeGreaterThanOrEqual(44);
    }
  });
}

test('replay, pause, intensity and intro controls', async ({ page }) => {
  await page.goto('/asia-holdings-logo-demo.html');
  const skip = page.locator('#skipEntry');
  if (await skip.isVisible()) await skip.click();
  await page.locator('#play').click();
  await expect(page.locator('#play')).toHaveAttribute('aria-pressed', 'true');
  await page.locator('#replay').click();
  await expect(page.locator('#play')).toHaveAttribute('aria-pressed', 'false');
  await page.locator('#level').click();
  await expect(page.locator('.stage')).toHaveAttribute('data-intensity', '4');
  await page.locator('#intro').click();
  await expect(page.locator('#intro')).toHaveAttribute('aria-pressed', 'true');
  await page.locator('#intro').click();
  await expect(page.locator('#intro')).toHaveAttribute('aria-pressed', 'false');
});

test('reduced motion prevents intro animation', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/asia-holdings-logo-demo.html');
  await page.locator('#intro').click();
  await expect(page.locator('#intro')).toHaveAttribute('aria-pressed', 'false');
  await expect(page.locator('.stage')).toHaveClass(/paused/);
});
