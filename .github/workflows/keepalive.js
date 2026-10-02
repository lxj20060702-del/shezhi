const { chromium } = require('playwright');

(async () => {
  const url = process.env.APP_URL;
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({
    viewport: { width: 375, height: 812 }
  });
  try {
    await page.goto(url, { timeout: 60000 });
    // 如果出现休眠按钮，自动点唤醒
    const wakeBtn = page.locator('text=Yes, get this app back up!');
    if (await wakeBtn.count() > 0) {
      await wakeBtn.click();
      console.log("✅已点击唤醒按钮");
    }
    // 在页面停留25秒，模拟真人
    await page.waitForTimeout(25000);
    console.log("✅访问完成");
  } catch (e) {
    console.error("❌出错:", e);
  } finally {
    await browser.close();
  }
})();
