from src.data_cleaning import load_and_clean
from src.neural_model import train_model

def main():
    print("🚀 Running Full AI Pipeline...")

    df = load_and_clean()     # all datasets processed
    train_model(df)           # real model training

    print("✅ DONE!")

if __name__ == "__main__":
    main()