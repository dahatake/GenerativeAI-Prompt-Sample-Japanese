// 研修用の架空コード(ExpenseFlow 深夜割増計算)。night_fare_cases.csv の「current_total_yen」を再現する。
package sample.expenseflow;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalTime;
import java.util.List;

public class ExpenseCalculator {

    private static final BigDecimal NIGHT_RATE = new BigDecimal("0.25");
    private static final BigDecimal MIDNIGHT_ALLOWANCE = new BigDecimal("120");

    public record Leg(LocalTime workStart, BigDecimal baseFare) {}

    /** 申請(複数区間)の合計金額を返す。 */
    public BigDecimal calculateTotal(List<Leg> legs) {
        BigDecimal total = BigDecimal.ZERO;
        for (Leg leg : legs) {
            total = total.add(calculateLeg(leg));
        }
        return total;
    }

    private BigDecimal calculateLeg(Leg leg) {
        BigDecimal baseFare = leg.baseFare();
        LocalTime workStart = leg.workStart();
        if (!NightAllowancePolicy.isNight(workStart)) {
            return baseFare;
        }
        BigDecimal nightRate = baseFare.multiply(NIGHT_RATE);
        BigDecimal subtotal = baseFare.add(nightRate);
        // 区間ごとに丸めているため、複数区間の申請で合計が1円ずれる
        subtotal = subtotal.setScale(0, RoundingMode.HALF_UP);
        if (workStart.isBefore(LocalTime.of(5, 0))) {
            subtotal = subtotal.add(MIDNIGHT_ALLOWANCE);
        }
        return subtotal;
    }
}
