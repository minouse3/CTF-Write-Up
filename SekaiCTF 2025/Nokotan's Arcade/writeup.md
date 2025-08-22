## Nokotan's Arcade - SekaiCTF 2025 Write-up

![Banner](assets/img/banner.png)

**Challenge:** Nokotan's Arcade
**Category:** Professional Programming & Coding (PPC)
**Points:** 100
**Author:** minouse3

### Introduction
This was actually my very first time running into a PPC (Professional Programming & Coding) challenge in a CTF event. Usually, I expect the standard crypto, pwn, or OSINT type problems, but here the focus was purely on coding under strict constraints. At first, it felt like a mix between a competitive programming contest and a CTF — which was both exciting and intimidating.

The challenge came with a PDF file, [**Nokotans_Arcade.pdf**](assets/files/Nokotans_Arcade.pdf), which contain the full problem statement, complete with background flavor text, sample cases, and constraints. At a glance, it looked exactly like a competitive programming task, but the catch was: you only get the flag after submitting the correct output-generating program.

### Analyzing the problem
The problem statement sets the scene: Nokotan owns an arcade with a Maimai machine, but only one screen works, so only one player can play at a time. Each game takes exactly `t` minutes, and every player who plays contributes a “popularity” score to the arcade.

We’re given the total arcade opening time `n`, the number of players `m`, and the game length `t`. Each player has their available time window `[li, ri]` and a popularity score `pi`. The task is to schedule games to maximize the total popularity value.

Constraints are tight (`n`, `m` up to 1e5, `pi` up to 1e9), so brute force is impossible — we need something efficient.

Breaking it down:
* A player can only play if their stay duration is at least `t`.
* Their possible start times are between `li` and `ri - t + 1`.
* At every minute, we might have multiple players available, but only one can actually play.
* We want the maximum total value, which means: pick the right player at the right time.

This is a classic setup for dynamic programming combined with a data structure to keep track of which players are available and which one gives the best reward.

### The Solution

We can solve it using a `multiset` in C++.
Preprocess players:
* For each `(l, r, p),` push `p` into `add[l]` (meaning this value becomes available at time `l`).
* Remove it at `r - t + 2`, because after that, the player doesn’t have enough time left to fit a full game.

Sweep time from 1 → n:
* Carry forward the best DP value.
* Update the active set by adding/removing popularity values as players enter/exit.
* If we can start a game at i, pick the best player (*active.rbegin()) and update:
```cpp
dp[i+t-1] = max(dp[i+t-1], dp[i-1] + best)
```

Answer: `dp[n]`
Here’s the code that does exactly that:
```cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m, t;
    cin >> n >> m >> t;

    vector<vector<ll>> add(n+2);

    for (int i = 0; i < m; i++) {
        int l, r; ll p;
        cin >> l >> r >> p;
        if (r - l + 1 >= t) {
            int L = l;
            int R = r - t + 1;
            add[L].push_back(p);
            if (R+1 <= n) add[R+1].push_back(-p);
        }
    }

    multiset<ll> active;
    vector<ll> dp(n+2, 0);

    for (int i = 1; i <= n; i++) {
        dp[i] = max(dp[i], dp[i-1]);

        for (ll v : add[i]) {
            if (v >= 0) active.insert(v);
            else active.erase(active.find(-v));
        }

        if (!active.empty() && i + t - 1 <= n) {
            ll best = *active.rbegin();
            dp[i+t-1] = max(dp[i+t-1], dp[i-1] + best);
        }
    }

    cout << dp[n] << "\n";
    return 0;
}
```
Runs in O((n + m) log m), which is fine under the 2s / 256MB limit.

### Flag
```
SEKAI{https://youtu.be/-PTe8zkYt9A}
```