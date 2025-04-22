# 🛡️ AI Antivirus

An intelligent, self-learning antivirus solution trained on imported `.dll` files, equipped with a PyQt-powered interface and an automatic quarantine system.

## ⚙️ Features

- 🤖 **AI Detection** – Machine learning model trained to detect malicious DLLs with high accuracy.
- 🔐 **Real-Time Scanning** – Monitors system activity and identifies suspicious DLL files.
- 📦 **Quarantine System** – Automatically isolates infected files to prevent harm.
- 🖥️ **PyQt GUI** – User-friendly interface for scanning, reviewing threats, and managing quarantine.
- 🧠 **Continuous Learning** – Regularly updated with new data to improve detection accuracy.

## 🖼️ UI Preview

> *(Add a screenshot here of the main PyQt GUI window once available)*

## 🧪 How It Works

1. **Data Input** – Loads and analyzes DLL files using static features.
2. **AI Model** – A custom-trained model classifies files as benign or malicious.
3. **Quarantine** – If flagged, files are moved to a secure quarantine folder.
4. **User Interface** – Lets users manually scan, manage quarantined files, and view logs.

## 🚀 Getting Started

### Requirements

- Python 3.9+
- PyQt5
- Scikit-learn / TensorFlow / (your ML lib)
- Pandas, NumPy
- `pefile` for parsing DLLs
- Any other dependencies your model requires

### Installation

```bash
git clone https://github.com/yourusername/ai-antivirus.git
cd ai-antivirus
pip install -r requirements.txt
python main.py
