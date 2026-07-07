
const calculate = (days: boolean[]) => {
    let num_days = 0;
    days.forEach((day) => (num_days += day ? 1 : 0));
    switch (num_days) {
        case 1:
            return 649;
        case 2:
            return 1099;
        case 3:
            return 1499;
        default:
            return 0;
    }
}

console.log("1 day:", calculate([true, false, false]));
console.log("2 days:", calculate([true, true, false]));
console.log("3 days:", calculate([true, true, true]));
console.log("0 days:", calculate([false, false, false]));
