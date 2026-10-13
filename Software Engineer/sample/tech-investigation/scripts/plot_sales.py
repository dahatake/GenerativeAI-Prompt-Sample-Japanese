from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

csv_path = Path("data") / "monthly_sales.csv"
df = pd.read_csv(csv_path)
summary = df.groupby("month", as_index=False)["sales_amount"].sum()
ax = summary.plot(x="month", y="sales_amount", kind="bar", title="Monthly Sales")
ax.figure.tight_layout()
plt.savefig("out/monthly_sales.png")
print(summary)
