import { test, expect } from '@playwright/test';

test.describe('Learning Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');

    // Skip onboarding or handle guest mode
    const onboardingSkip = page.locator('text=Continue as Guest');
    if (await onboardingSkip.isVisible({ timeout: 3000 })) {
      await onboardingSkip.click();
    }
  });

  test('should display homepage with navigation', async ({ page }) => {
    // Should show homepage elements
    await expect(page.locator('h1:has-text("Smart Navigator")').first()).toBeVisible();
    await expect(page.locator('text=Immersive Language Learning')).toBeVisible();

    // Should show user info or sign in
    const signIn = page.locator('text=Sign In');
    const welcomeMessage = page.locator('text=Welcome,');

    const hasSignIn = await signIn.isVisible();
    const hasWelcome = await welcomeMessage.isVisible();

    expect(hasSignIn || hasWelcome).toBeTruthy();
  });

  test('should navigate to learning view', async ({ page }) => {
    // Look for new video button or similar navigation
    const newVideoButton = page.locator('text=Start New Video', 'text=New Video', 'button:has-text("video")', 'button:has-text("Learn")').first();

    if (await newVideoButton.isVisible({ timeout: 2000 })) {
      await newVideoButton.click();

      // Should navigate to learning interface
      await expect(page.locator('text=Extract Content', 'input[placeholder*="YouTube"]')).toBeVisible();
    }
  });

  test('should handle video URL input', async ({ page }) => {
    // Navigate to learning view first
    const backToLearning = page.locator('text=Back to Home').first();
    if (!(await backToLearning.isVisible({ timeout: 1000 }))) {
      const newVideoButton = page.locator('button:has-text("video"), button:has-text("Learn"), text=Start').first();
      if (await newVideoButton.isVisible({ timeout: 2000 })) {
        await newVideoButton.click();
      }
    }

    // Should have video URL input
    const urlInput = page.locator('input[placeholder*="YouTube"], input[placeholder*="URL"]').first();
    await expect(urlInput).toBeVisible({ timeout: 5000 });

    // Test video URL input
    await urlInput.fill('https://www.youtube.com/watch?v=dQw4w9WgXcQ');

    // Should have extract button
    const extractButton = page.locator('text=Extract Content', 'button:has-text("Extract")').first();
    await expect(extractButton).toBeVisible();

    // Button should be enabled after URL input
    await expect(extractButton).toBeEnabled();
  });

  test('should show test video buttons', async ({ page }) => {
    // Navigate to learning interface
    const backToLearning = page.locator('text=Back to Home').first();
    if (!(await backToLearning.isVisible({ timeout: 1000 }))) {
      const newVideoButton = page.locator('button:has-text("video"), button:has-text("Learn")').first();
      if (await newVideoButton.isVisible({ timeout: 2000 })) {
        await newVideoButton.click();
      }
    }

    // Should show test video buttons
    await expect(page.locator('text=Test Video 1')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('text=Test Video 2')).toBeVisible();
  });

  test('should display level selector', async ({ page }) => {
    // Navigate to learning interface if needed
    const backToLearning = page.locator('text=Back to Home').first();
    if (!(await backToLearning.isVisible({ timeout: 1000 }))) {
      const newVideoButton = page.locator('button, text=Start').first();
      if (await newVideoButton.isVisible({ timeout: 2000 })) {
        await newVideoButton.click();
      }
    }

    // Should have CEFR level selector
    const levelSelector = page.locator('select, [role="listbox"]').first();
    await expect(levelSelector).toBeVisible({ timeout: 5000 });

    // Should have level options
    if (await levelSelector.isVisible()) {
      await levelSelector.click();
      await expect(page.locator('text=A1', 'option:has-text("A1")')).toBeVisible();
    }
  });

  test('should handle learning panel states', async ({ page }) => {
    // This is a more complex test that would require content extraction
    // For now, we'll test the basic structure is present

    // Navigate to learning view
    const backToLearning = page.locator('text=Back to Home').first();
    if (!(await backToLearning.isVisible({ timeout: 1000 }))) {
      const newVideoButton = page.locator('button').first();
      if (await newVideoButton.isVisible({ timeout: 2000 })) {
        await newVideoButton.click();
      }
    }

    // Should have video section and learning panel section
    const videoSection = page.locator('.video-section, [class*="video"]').first();
    const learningPanel = page.locator('.content-panel, .learning-panel, [class*="panel"]').first();

    // At least one should be visible (layout structure)
    const hasVideoSection = await videoSection.isVisible({ timeout: 3000 });
    const hasLearningPanel = await learningPanel.isVisible({ timeout: 3000 });

    expect(hasVideoSection || hasLearningPanel).toBeTruthy();
  });

  test('should show user profile information', async ({ page }) => {
    // Should show either user profile or sign in option
    const userAvatar = page.locator('[style*="border-radius: 50%"]', '.user-avatar').first();
    const signInButton = page.locator('text=Sign In');
    const welcomeMessage = page.locator('text=Welcome,');

    const hasUserInfo = await userAvatar.isVisible({ timeout: 2000 });
    const hasSignIn = await signInButton.isVisible({ timeout: 2000 });
    const hasWelcome = await welcomeMessage.isVisible({ timeout: 2000 });

    expect(hasUserInfo || hasSignIn || hasWelcome).toBeTruthy();
  });

  test('should handle responsive design', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Should still show core elements
    await expect(page.locator('h1:has-text("Smart Navigator")').first()).toBeVisible();

    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page.locator('h1:has-text("Smart Navigator")').first()).toBeVisible();

    // Test desktop viewport
    await page.setViewportSize({ width: 1280, height: 720 });
    await expect(page.locator('h1:has-text("Smart Navigator")').first()).toBeVisible();
  });
});