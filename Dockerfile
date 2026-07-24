FROM python:3.8

# Setup tmp (biar aman di container)
RUN mkdir -p /tmp && chmod 1777 /tmp
ENV TMPDIR=/tmp

# Install dependencies dasar
# (Xvfb & libgtk-3-0 dihapus karena Chrome jalan --headless=new, tidak butuh virtual display)
RUN apt-get update && apt-get install -y \
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

RUN wget -O /tmp/chrome.zip https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chrome-linux64.zip \
    && unzip /tmp/chrome.zip -d /opt/ \
    && ln -s /opt/chrome-linux64/chrome /usr/bin/google-chrome \
    && rm /tmp/chrome.zip

RUN wget -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip \
    && unzip /tmp/chromedriver.zip -d /opt/ \
    && ln -s /opt/chromedriver-linux64/chromedriver /usr/bin/chromedriver \
    && rm /tmp/chromedriver.zip

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

# Run
CMD ["/run.sh"]
