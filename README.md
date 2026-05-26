# Stock Return Prediction and LQ45 Portfolio Construction Using LSTM and BiLSTM Models Based on Technical Indicators and News Sentiment

This repository contains the source code, datasets, and visualization plots for the thesis research on predicting LQ45 index stock returns using a multimodal deep learning approach (LSTM & BiLSTM) integrated with technical indicators and online news sentiment.

## 📌 Project Overview
This study evaluates and compares the performance of **LSTM** and **BiLSTM** architectures across three main experimental scenarios:
1. **Univariate Scenario:** Utilizing only historical daily closing prices as the baseline feature.
2. **Multivariate (Technical) Scenario:** Integrating stock prices with technical indicators.
3. **Multivariate (Sentiment) Scenario:** Combining technical indicators with news sentiment scores extracted from Investing.com.

Ultimately, the return projections from the optimal model (BiLSTM + Sentiment) are implemented to construct 10 variations of optimal investment portfolios ($k=2$ to $k=10$) based on Markowitz's Portfolio Theory.

---

## 📂 Repository Structure
For ease of navigation, the repository is organized into the following directories:

├── dataset/                           # Datasets (.csv) for stock prices & news text
├── code/                              # Code (.ipynb and .py) for model training and evaluation
│   ├── LSTM_BiLSTM_Univariate.ipynb
│   ├── LSTM_BiLSTM_Multivariate.ipynb
│   ├── LSTM_BiLSTM_Multivariate_+_Sentiment.ipynb
│   └── Sentiment Analysis VADER.py
├── result/                            # Visualization plots for all 45 LQ45 stocks
│   ├── univariate/                    # Predicted vs Actual plots for the univariate scenario
│   ├── multivariate/                  # Predicted vs Actual plots for the multivariate technical scenario
│   └── multivariate + sentiment/      # Predicted vs Actual plots for the best-performing model (BiLSTM + Sentiment)
└── README.md                          

---

## 🛠️ Environment
The experiments were conducted in a cloud-based **Google Colab (GPU Accelerated)** environment. The implementation relies on the following core Python libraries:
* **Python 3.x**
* **TensorFlow & Keras** (Deep Learning Modeling)
* **Pandas & NumPy** (Time-Series Data Manipulation)
* **Scikit-Learn** (Evaluation Metrics: MAE, RMSE, NMSE, $R^2$)
* **VADER** (Text Processing & Sentiment Score Extraction)

---

## 👤 Author
* **Joanna Ayulia Benyamin**
* Department of Computational Science, Faculty of Mathematics and Natural Sciences, Institut Teknologi Bandung, 40132
