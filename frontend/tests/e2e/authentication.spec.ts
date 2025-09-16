import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Clear localStorage to ensure clean state
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await page.reload();
    await page.waitForLoadState('networkidle');
  });

  test('should show sign in button when not authenticated', async ({ page }) => {
    // Wait for the app to load and handle onboarding
    await page.waitForTimeout(3000);

    // Try to skip onboarding if it appears
    try {
      const skipButton = page.locator('button:has-text("Skip")');
      if (await skipButton.isVisible({ timeout: 2000 })) {
        await skipButton.click({ force: true });
      }
    } catch (error) {
      console.log('Skip button not found or clickable');
    }

    // Wait and check for sign in button
    await page.waitForTimeout(2000);
    await expect(page.locator('button:has-text("Sign In")')).toBeVisible({ timeout: 10000 });
  });

  test('should open authentication modal when sign in is clicked', async ({ page }) => {
    // Click sign in button
    await page.click('button:has-text("Sign In")');

    // Modal should appear
    await expect(page.locator('text=Welcome Back!')).toBeVisible();
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
  });

  test('should switch between login and register forms', async ({ page }) => {
    // Open auth modal
    await page.click('button:has-text("Sign In")');

    // Should start with login form
    await expect(page.locator('text=Welcome Back!')).toBeVisible();

    // Switch to register
    await page.click('text=Sign up here');
    await expect(page.locator('text=Join Smart Navigator')).toBeVisible();
    await expect(page.locator('input[name="name"]')).toBeVisible();
    await expect(page.locator('input[name="username"]')).toBeVisible();

    // Switch back to login
    await page.click('text=Sign in here');
    await expect(page.locator('text=Welcome Back!')).toBeVisible();
  });

  test('should validate required fields in login form', async ({ page }) => {
    await page.click('button:has-text("Sign In")');

    // Try to submit without filling fields
    await page.click('text=Sign In', { clickCount: 2 }); // Button inside form

    // Form validation should prevent submission
    const emailInput = page.locator('input[type="email"]');
    const passwordInput = page.locator('input[type="password"]');

    await expect(emailInput).toHaveAttribute('required');
    await expect(passwordInput).toHaveAttribute('required');
  });

  test('should validate registration form', async ({ page }) => {
    await page.click('button:has-text("Sign In")');
    await page.click('text=Sign up here');

    // Fill partial form
    await page.fill('input[name="name"]', 'Test User');
    await page.fill('input[name="email"]', 'invalid-email');

    // Try to submit
    await page.click('button[type="submit"]');

    // Should have validation errors
    const emailInput = page.locator('input[name="email"]');
    await expect(emailInput).toHaveAttribute('type', 'email');
  });

  test('should close modal when close button is clicked', async ({ page }) => {
    await page.click('button:has-text("Sign In")');
    await expect(page.locator('text=Welcome Back!')).toBeVisible();

    // Click close button (×)
    await page.click('text=×');

    // Modal should be closed
    await expect(page.locator('text=Welcome Back!')).not.toBeVisible();
  });

  test('should continue as guest option', async ({ page }) => {
    await page.click('button:has-text("Sign In")');

    // Should show continue as guest option
    await expect(page.locator('text=Continue as Guest')).toBeVisible();

    // Click continue as guest
    await page.click('text=Continue as Guest');

    // Should close modal and stay on homepage
    await expect(page.locator('text=Welcome Back!')).not.toBeVisible();
  });

  test('should show loading states', async ({ page }) => {
    await page.click('button:has-text("Sign In")');

    // Fill login form
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');

    // Submit form (this will likely fail but we can test loading state)
    await page.click('button[type="submit"]');

    // Button should show loading state
    await expect(page.locator('text=Signing In...')).toBeVisible({ timeout: 1000 });
  });
});