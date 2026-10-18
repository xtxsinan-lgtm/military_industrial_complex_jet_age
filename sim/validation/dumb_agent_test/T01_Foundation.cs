using System;
using System.Collections.Generic;
using System.Text;

namespace MIC.Core.Random;

public static class Fnv1a64
{
    public const ulong OffsetBasis = 0xCBF29CE484222325UL;
    public const ulong Prime = 0x00000100000001B3UL;

    public static ulong HashStreamName(string streamName)
    {
        byte[] bytes = Encoding.UTF8.GetBytes(streamName);
        ulong hash = OffsetBasis;
        unchecked
        {
            foreach (byte b in bytes)
            {
                hash = (hash ^ b) * Prime;
            }
        }
        return hash;
    }

    public static string ToHex(ulong value) => $"0x{value:x16}";

    public static ulong FromHex(string hexValue)
    {
        if (hexValue.StartsWith("0x", StringComparison.OrdinalIgnoreCase))
        {
            hexValue = hexValue.Substring(2);
        }
        return Convert.ToUInt64(hexValue, 16);
    }
}

public sealed class Pcg32
{
    public const ulong Multiplier = 6364136223846793005UL;
    public ulong State { get; private set; }
    public ulong Inc { get; private set; }

    public Pcg32(ulong initState = 0x853C49E6748FEA9BUL, ulong initSeq = 0xDA3E39CB94B95BDBUL)
    {
        Seed(initState, initSeq);
    }

    public static Pcg32 FromRawState(ulong state, ulong inc)
    {
        var pcg = new Pcg32(0, 0);
        pcg.State = state;
        pcg.Inc = inc;
        return pcg;
    }

    public void Seed(ulong initState, ulong initSeq)
    {
        unchecked
        {
            State = 0UL;
            Inc = (initSeq << 1) | 1UL;
            NextU32();
            State += initState;
            NextU32();
        }
    }

    public uint NextU32()
    {
        unchecked
        {
            ulong oldstate = State;
            State = oldstate * Multiplier + Inc;
            uint xorshifted = (uint)(((oldstate >> 18) ^ oldstate) >> 27);
            int rot = (int)(oldstate >> 59);
            return (xorshifted >> rot) | (xorshifted << ((-rot) & 31));
        }
    }

    public ulong NextU64()
    {
        uint hi = NextU32();
        uint lo = NextU32();
        return ((ulong)hi << 32) | lo;
    }

    public double NextFloat()
    {
        return (NextU64() >> 11) * (1.0 / (1UL << 53));
    }

    public uint NextBounded(uint bound)
    {
        unchecked
        {
            uint threshold = (uint)((0UL - bound) % bound);
            while (true)
            {
                uint r = NextU32();
                if (r >= threshold)
                {
                    return r % bound;
                }
            }
        }
    }

    public double Uniform(double low, double high)
    {
        return low + (high - low) * NextFloat();
    }

    public int RandInt(int lowInclusive, int highInclusive)
    {
        uint span = (uint)(highInclusive - lowInclusive + 1);
        return lowInclusive + (int)NextBounded(span);
    }

    public bool Bernoulli(double p)
    {
        return NextFloat() < p;
    }

    public double Normal(double mu = 0.0, double sigma = 1.0)
    {
        double u1 = Math.Max(NextFloat(), 1.1102230246251565e-16);
        double u2 = NextFloat();
        double z0 = Math.Sqrt(-2.0 * Math.Log(u1)) * Math.Cos(2.0 * Math.PI * u2);
        return mu + sigma * z0;
    }

    public T Choice<T>(IReadOnlyList<T> items)
    {
        if (items == null || items.Count == 0) throw new ArgumentException("Items cannot be empty");
        uint idx = NextBounded((uint)items.Count);
        return items[(int)idx];
    }

    public T WeightedChoice<T>(IReadOnlyList<T> items, IReadOnlyList<double> weights)
    {
        if (items == null || weights == null || items.Count == 0 || items.Count != weights.Count)
            throw new ArgumentException("Invalid items or weights");
        double total = 0.0;
        foreach (var w in weights) total += w;
        double r = NextFloat() * total;
        double upto = 0.0;
        for (int i = 0; i < items.Count; i++)
        {
            upto += weights[i];
            if (upto >= r) return items[i];
        }
        return items[items.Count - 1];
    }

    public void ShuffleInPlace<T>(IList<T> items)
    {
        for (int i = items.Count - 1; i > 0; i--)
        {
            uint j = NextBounded((uint)(i + 1));
            T tmp = items[i];
            items[i] = items[(int)j];
            items[(int)j] = tmp;
        }
    }

    public static double MtthProb(double mtthDays, double dtDays)
    {
        return 1.0 - Math.Pow(2.0, -dtDays / mtthDays);
    }

    public Pcg32StateDto ToDto() => new Pcg32StateDto(Fnv1a64.ToHex(State), Fnv1a64.ToHex(Inc));

    public static Pcg32 FromDto(Pcg32StateDto dto)
    {
        return FromRawState(Fnv1a64.FromHex(dto.State), Fnv1a64.FromHex(dto.Inc));
    }
}

public sealed record Pcg32StateDto(string State, string Inc);

namespace MIC.Core.Random;
using System.Collections.Generic;

public sealed class RngStreamRegistry
{
    public ulong MasterSeed { get; }

    public RngStreamRegistry(ulong masterSeed)
    {
        MasterSeed = masterSeed;
    }

    public Pcg32 Stream(string name)
    {
        ulong h = Fnv1a64.HashStreamName(name);
        ulong initState = MasterSeed ^ h;
        ulong initSeq = h;
        return new Pcg32(initState, initSeq);
    }

    public RngRegistryDto ToDto()
    {
        return new RngRegistryDto(Fnv1a64.ToHex(MasterSeed), new Dictionary<string, Pcg32StateDto>());
    }

    public static RngStreamRegistry FromDto(RngRegistryDto dto)
    {
        return new RngStreamRegistry(Fnv1a64.FromHex(dto.MasterSeed));
    }
}

public sealed record RngRegistryDto(string MasterSeed, IReadOnlyDictionary<string, Pcg32StateDto> Streams);

namespace MIC.Core.Calendar;

public readonly record struct SimDate(int Year, int Month, int DayOfMonth)
{
    public int ToDayIndex() => GameCalendar.YmdToDay(Year, Month, DayOfMonth);
    public static SimDate FromDayIndex(int dayIndex) => GameCalendar.DayToYmd(dayIndex);
    public override string ToString() => $"{Year:D4}-{Month:D2}-{DayOfMonth:D2}";
}

public sealed record TickSchedule(
    int Day, int Year, int Month, int DayOfMonth, string Iso, int Weekday,
    int CalendarQuarter, int FiscalYear, int FiscalQuarter,
    bool IsMonthStart, bool IsMonthEnd, bool IsQuarterStart,
    bool IsFiscalQuarterStart, bool IsYearStart, bool IsFiscalYearStart,
    int DaysInCurrentMonth, int DaysInPrevMonth
);

public static class GameCalendar
{
    public const int CivilOffset19450101 = 710337;
    public const int CampaignStartDay = 0;
    public const int CampaignEndDay = 5843;

    public static bool IsLeapYear(int year)
    {
        return year % 4 == 0 && (year % 100 != 0 || year % 400 == 0);
    }

    public static int DaysInMonth(int year, int month)
    {
        int[] days = { 0, 31, IsLeapYear(year) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };
        return days[month];
    }

    public static int YmdToDay(int year, int month, int day)
    {
        int y = year;
        if (month <= 2) y--;
        int era = (y >= 0 ? y : y - 399) / 400;
        int yoe = y - era * 400;
        int moy = month;
        if (month > 2) moy -= 3;
        else moy += 9;
        int doy = (153 * moy + 2) / 5 + day - 1;
        int doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
        int daysFromCiv = era * 146097 + doe - 719468;
        return daysFromCiv - CivilOffset19450101;
    }

    public static SimDate DayToYmd(int dayIndex)
    {
        int z = dayIndex + CivilOffset19450101 + 719468;
        int era = (z >= 0 ? z : z - 146096) / 146097;
        int doe = z - era * 146097;
        int yoe = (doe - doe / 1460 + doe / 38440 - doe / 146096) / 365;
        int y = yoe + era * 400;
        int doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
        int mp = (5 * doy + 2) / 153;
        int d = doy - (153 * mp + 2) / 5 + 1;
        int m = mp < 10 ? mp + 3 : mp - 9;
        y += (m <= 2 ? 1 : 0);
        return new SimDate(y, m, d);
    }

    public static string DayToIso(int dayIndex)
    {
        var dt = DayToYmd(dayIndex);
        return dt.ToString();
    }

    public static int IsoToDay(string isoDate)
    {
        var parts = isoDate.Split('-');
        return YmdToDay(int.Parse(parts[0]), int.Parse(parts[1]), int.Parse(parts[2]));
    }

    public static int Weekday(int dayIndex)
    {
        return (dayIndex % 7 + 7) % 7;
    }

    public static (int FiscalYear, int FiscalQuarter) GetFiscalYearAndQuarter(int year, int month)
    {
        if (month >= 7)
        {
            int fy = year + 1;
            int fq = (month - 7) / 3 + 1;
            return (fy, fq);
        }
        else
        {
            int fy = year;
            int fq = (month + 5) / 3 + 1;
            return (fy, fq);
        }
    }

    public static (int StartDay, int EndDay) FiscalYearBounds(int fiscalYear)
    {
        int startDay = YmdToDay(fiscalYear - 1, 7, 1);
        int endDay = YmdToDay(fiscalYear, 6, 30);
        return (startDay, endDay);
    }

    public static int AddMonths(int dayIndex, int months)
    {
        var dt = DayToYmd(dayIndex);
        int totalM = dt.Year * 12 + (dt.Month - 1) + months;
        int ny = totalM / 12;
        int nm = (totalM % 12) + 1;
        int nd = Math.Min(dt.DayOfMonth, DaysInMonth(ny, nm));
        return YmdToDay(ny, nm, nd);
    }

    public static TickSchedule GetTickSchedule(int dayIndex)
    {
        var dt = DayToYmd(dayIndex);
        string iso = dt.ToString();
        int wd = Weekday(dayIndex);
        int cq = (dt.Month - 1) / 3 + 1;
        var (fy, fq) = GetFiscalYearAndQuarter(dt.Year, dt.Month);
        int dim = DaysInMonth(dt.Year, dt.Month);
        int prevM = dt.Month == 1 ? 12 : dt.Month - 1;
        int prevY = dt.Month == 1 ? dt.Year - 1 : dt.Year;
        int dpdim = DaysInMonth(prevY, prevM);

        return new TickSchedule(
            Day: dayIndex,
            Year: dt.Year,
            Month: dt.Month,
            DayOfMonth: dt.DayOfMonth,
            Iso: iso,
            Weekday: wd,
            CalendarQuarter: cq,
            FiscalYear: fy,
            FiscalQuarter: fq,
            IsMonthStart: dt.DayOfMonth == 1,
            IsMonthEnd: dt.DayOfMonth == dim,
            IsQuarterStart: dt.DayOfMonth == 1 && (dt.Month == 1 || dt.Month == 4 || dt.Month == 7 || dt.Month == 10),
            IsFiscalQuarterStart: dt.DayOfMonth == 1 && (dt.Month == 7 || dt.Month == 10 || dt.Month == 1 || dt.Month == 4),
            IsYearStart: dt.Month == 1 && dt.DayOfMonth == 1,
            IsFiscalYearStart: dt.Month == 7 && dt.DayOfMonth == 1,
            DaysInCurrentMonth: dim,
            DaysInPrevMonth: dpdim
        );
    }
}
