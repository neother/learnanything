// Frontend logging service that outputs to both console and a log file (via Node.js when available)

export interface LogEntry {
  timestamp: string;
  level: 'INFO' | 'WARN' | 'ERROR' | 'DEBUG';
  message: string;
  data?: any;
}

class Logger {
  private logHistory: LogEntry[] = [];
  private maxHistorySize = 1000;

  private formatTimestamp(): string {
    return new Date().toISOString();
  }

  private createLogEntry(level: LogEntry['level'], message: string, data?: any): LogEntry {
    const entry: LogEntry = {
      timestamp: this.formatTimestamp(),
      level,
      message,
      data
    };

    // Add to history
    this.logHistory.push(entry);
    if (this.logHistory.length > this.maxHistorySize) {
      this.logHistory.shift();
    }

    return entry;
  }

  private writeToConsole(entry: LogEntry): void {
    const logMessage = `${entry.timestamp} [${entry.level}] ${entry.message}`;

    switch (entry.level) {
      case 'ERROR':
        console.error(logMessage, entry.data || '');
        break;
      case 'WARN':
        console.warn(logMessage, entry.data || '');
        break;
      case 'DEBUG':
        console.debug(logMessage, entry.data || '');
        break;
      default:
        console.log(logMessage, entry.data || '');
    }
  }

  private async writeToFile(entry: LogEntry): Promise<void> {
    // Only works in Node.js environment (development server)
    if (typeof window !== 'undefined') {
      // We're in browser - try to send to development server for file logging
      try {
        await fetch('/api/log', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(entry)
        });
      } catch (error) {
        // Silently fail if logging endpoint is not available
        // This is expected in production builds
      }
    }
  }

  public info(message: string, data?: any): void {
    const entry = this.createLogEntry('INFO', message, data);
    this.writeToConsole(entry);
    this.writeToFile(entry);
  }

  public warn(message: string, data?: any): void {
    const entry = this.createLogEntry('WARN', message, data);
    this.writeToConsole(entry);
    this.writeToFile(entry);
  }

  public error(message: string, data?: any): void {
    const entry = this.createLogEntry('ERROR', message, data);
    this.writeToConsole(entry);
    this.writeToFile(entry);
  }

  public debug(message: string, data?: any): void {
    const entry = this.createLogEntry('DEBUG', message, data);
    this.writeToConsole(entry);
    this.writeToFile(entry);
  }

  public getLogHistory(): LogEntry[] {
    return [...this.logHistory];
  }

  public clearHistory(): void {
    this.logHistory = [];
  }

  public exportLogs(): string {
    return this.logHistory
      .map(entry => `${entry.timestamp} [${entry.level}] ${entry.message}${entry.data ? ' | ' + JSON.stringify(entry.data) : ''}`)
      .join('\n');
  }
}

// Export singleton instance
export const logger = new Logger();

// Override console methods in development to also log to file
if (process.env.NODE_ENV === 'development') {
  const originalConsoleLog = console.log;
  const originalConsoleWarn = console.warn;
  const originalConsoleError = console.error;

  console.log = (...args) => {
    originalConsoleLog(...args);
    logger.info(args.join(' '));
  };

  console.warn = (...args) => {
    originalConsoleWarn(...args);
    logger.warn(args.join(' '));
  };

  console.error = (...args) => {
    originalConsoleError(...args);
    logger.error(args.join(' '));
  };
}