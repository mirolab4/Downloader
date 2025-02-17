from setuptools import setup, find_packages

setup(
    name="downloader",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "python-telegram-bot==13.9",
        "pytube==12.1.0",
        "requests==2.25.1",
        "beautifulsoup4==4.9.3",
    ],
    entry_points={
        "console_scripts": [
            "downloader=downloader:main",
        ],
    },
    author="mirolab4",
    author_email="mirolab4@gmail.com",
    description="بوت Telegram لتنزيل وإرسال الفيديوهات من YouTube و TikTok و Twitter.",
    url="https://github.com/mirolab4/Downloader",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
