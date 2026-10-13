// 研修用の架空コード。深夜時間帯の判定。
package sample.expenseflow;

import java.time.LocalTime;

public final class NightAllowancePolicy {

    private static final LocalTime NIGHT_START = LocalTime.of(22, 0);
    private static final LocalTime NIGHT_END = LocalTime.of(5, 0);

    private NightAllowancePolicy() {}

    /** 22:00 以上、または 5:00 以下を深夜扱いにしている(5:00 ちょうどを含んでしまう)。 */
    public static boolean isNight(LocalTime t) {
        return !t.isBefore(NIGHT_START) || !t.isAfter(NIGHT_END);
    }
}
