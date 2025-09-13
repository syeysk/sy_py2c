int ac = 6;
float ab = 9;
string hello(int a, int b) {
    return (a + b > 0) ? "good" : "not good";
}
string hello(int a) {
    return hello(a, 5);
}
