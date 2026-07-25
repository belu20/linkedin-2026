FROM python:3.11-slim

# Setup tmp (biar aman di container)
RUN mkdir -p /tmp && chmod 1777 /tmp
ENV TMPDIR=/tmp

# Install dependencies dasar
# (Xvfb & libgtk-3-0 dihapus karena Chrome jalan --headless=new, tidak butuh virtual display)
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    unzip \
    curl \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libxss1 \
    libasound2 \
    libgbm1 \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome for Testing + matching Chromedriver (VERSI SAMA)
ENV CHROME_VERSION=147.0.7727.116

# Digabung jadi satu layer supaya image lebih ringkas
RUN wget -q -O /tmp/chrome.zip https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chrome-linux64.zip \
    && unzip -q /tmp/chrome.zip -d /opt/ \
    && ln -s /opt/chrome-linux64/chrome /usr/bin/google-chrome \
    && wget -q -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip \
    && unzip -q /tmp/chromedriver.zip -d /opt/ \
    && ln -s /opt/chromedriver-linux64/chromedriver /usr/bin/chromedriver \
    && rm /tmp/chrome.zip /tmp/chromedriver.zip

# Install Python libs dari requirements.txt
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy source code
COPY run.sh /
COPY setting.py /
COPY api.py /
COPY src/ /src/
# COPY accounts.json /

# Permission
RUN chmod +x /run.sh

# Jalankan sebagai non-root user (praktik keamanan lebih baik untuk container long-running)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /src /run.sh /setting.py /api.py
USER appuser

# Healthcheck ke endpoint status Flask
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT:-5000}/status || exit 1

# Run
CMD ["/run.sh"]