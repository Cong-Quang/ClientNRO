using System;
class Program {
    static void Main() {
        long val1 = 9084277218871345152;
        Console.WriteLine(BitConverter.Int64BitsToDouble(val1));
        long val2 = 2642282713930792960;
        Console.WriteLine(BitConverter.Int64BitsToDouble(val2));
    }
}
