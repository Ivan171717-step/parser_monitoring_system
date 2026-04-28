class ScrapingBlockedError(RuntimeError):
    """Raised when website blocks scraping: 403, 429, CAPTCHA, etc."""
