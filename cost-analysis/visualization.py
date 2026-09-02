"""
Столбчатая диаграмма: суммарные затраты на автоматизацию vs ручное тестирование
за 234 тестовых цикла (итоговые цифры из аналитической части ВКР).
"""
import matplotlib.pyplot as plt

labels = ["Автоматизация", "Ручное тестирование"]
values = [2489160, 5776316]

plt.figure(figsize=(8, 6))
bars = plt.bar(labels, values, color=["skyblue", "salmon"])
plt.ylabel("Затраты (руб.)")
plt.title("Сравнение затрат на автоматизацию и ручное тестирование")

for bar in bars:
    height = bar.get_height()
    plt.annotate(
        f"{height:,.0f}",
        xy=(bar.get_x() + bar.get_width() / 2, height),
        xytext=(0, 5),
        textcoords="offset points",
        ha="center",
        va="bottom",
    )

ax = plt.gca()
ax.ticklabel_format(style="plain", axis="y")

if __name__ == "__main__":
    plt.savefig("cost_comparison.png", dpi=150, bbox_inches="tight")
    print("Сохранено: cost_comparison.png")
