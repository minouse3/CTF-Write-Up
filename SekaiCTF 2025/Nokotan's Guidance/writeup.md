## constructor - idekCTF 2025 Write-up

![Banner](assets/img/banner.png)

**Challenge:** constructor
**Category:** Reverse
**Points:** 100
**Author:** minouse3

### Introduction
This was the second PPC problem I tried in the event, and honestly, I pretty liked it. After solving the first PPC, I started to get used to the style — they feel just like competitive programming problems but packaged inside a CTF. It was different from the usual pwn/crypto challenges, but in a good way.

The PDF, [**Nokotans_Guidance.pdf**](assets/files/Nokotans_Guidance.pdf) described this quirky “triangle graph” world. At first glance it looked intimidating: start with a triangle of nodes {1,2,3}, then every new node gets attached to an existing edge to form another triangle. With up to 150k nodes and 150k queries, the challenge was asking for shortest paths between nodes in this huge structure.

What I enjoyed was that once I stared at it long enough, I realized the structure isn’t arbitrary at all. It’s actually a tree of triangles, and that made the problem not only solvable, but really elegant.

### Analyzing the problem
The graph grows in a very structured way. Every new node always forms a triangle with an existing edge. That means the graph is not arbitrary — it’s actually a tree of triangles (each triangle is like a “clique node” in a bigger tree).

The queries boil down to:
* Each node belongs to exactly one triangle.
* If we know which triangles two nodes belong to, then the shortest path between them passes through the Lowest Common Ancestor (LCA) triangle in this tree.

So the plan becomes:

1. Build this tree of triangles as the graph grows.
2. Precompute parents and distances using binary lifting.
3. For each query `(s, t)`, jump both up to their LCA and compute the shortest path.

But there’s one catch: each triangle has three vertices, and distances can shift depending on which vertex we enter/exit from. To handle that, we need 3×3 transfer matrices that encode the cost of moving between triangles.

### The solution
The solution looks complicated at first, but it boils down to a few key tricks:

1. **Triangles as nodes:** Every triangle is treated as one “super node” in a tree. Node `i` belongs to a triangle, and that triangle is its “anchor.”
2. **Transfer matrices:** Between two adjacent triangles, we build a 3×3 matrix `M` where `M[i][j]` is the cost to enter from vertex `i` of triangle A and leave from vertex `j` of triangle B. Inside one triangle, distances are trivial (0 if same vertex, 1 otherwise).
3. **Binary lifting with matrices:** For each triangle, we store not just its 2^k ancestor but also a matrix that tells us the cost of jumping that far up. When we lift a query node up the tree, we multiply its vector of distances by these matrices using min-plus algebra.
4. **Answering queries:** For each query, we turn both nodes into 3-element vectors (0 at their own position, INF elsewhere), lift them up to their LCA triangle using the precomputed matrices, and then at the LCA we check all vertex pairs `(i, j)` to calculate the total cost — the smallest of these values is the shortest path between the two nodes.

Here’s the code that puts it all together:
```cpp
#include <bits/stdc++.h>
using namespace std;

static const int INF = 0x3f3f3f3f;

struct Mat3 {
    int a[3][3];
    Mat3(int diag = 0) {
        for (int i=0;i<3;i++) for (int j=0;j<3;j++) a[i][j] = (i==j ? diag : (diag==0 ? INF : INF));
    }
};
inline int triDistIdx(int i, int j) { return (i==j ? 0 : 1); }

inline Mat3 minplus_mul(const Mat3& A, const Mat3& B) {
    Mat3 C;
    for (int i=0;i<3;i++) for (int j=0;j<3;j++) C.a[i][j] = INF;
    for (int i=0;i<3;i++) {
        for (int k=0;k<3;k++) {
            int aik = A.a[i][k];
            if (aik >= INF) continue;
            const int* bk = B.a[k];
            int v0 = aik + bk[0];
            int v1 = aik + bk[1];
            int v2 = aik + bk[2];
            if (v0 < C.a[i][0]) C.a[i][0] = v0;
            if (v1 < C.a[i][1]) C.a[i][1] = v1;
            if (v2 < C.a[i][2]) C.a[i][2] = v2;
        }
    }
    return C;
}

inline array<int,3> vec_minplus_mul(const array<int,3>& v, const Mat3& M) {
    array<int,3> r{INF, INF, INF};
    for (int k=0;k<3;k++) {
        int vk = v[k];
        if (vk >= INF) continue;
        int v0 = vk + M.a[k][0];
        int v1 = vk + M.a[k][1];
        int v2 = vk + M.a[k][2];
        if (v0 < r[0]) r[0] = v0;
        if (v1 < r[1]) r[1] = v1;
        if (v2 < r[2]) r[2] = v2;
    }
    return r;
}

static inline uint64_t ekey(int x, int y){
    if (x>y) swap(x,y);
    return ( (uint64_t)x << 32 ) | (uint32_t)y;
}

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    if(!(cin>>n)) return 0;

    // Triangles (cliques) tree: ids 1..T where T = n-2
    int Tn = n - 2;
    vector<array<int,3>> tri(Tn+1);
    tri[1] = {1,2,3};

    // track "last triangle" for each edge to connect new triangle
    unordered_map<uint64_t,int> last;
    last.reserve(3*n);
    last[ekey(1,2)] = 1;
    last[ekey(2,3)] = 1;
    last[ekey(1,3)] = 1;

    // clique-tree adjacency with per-edge 3x3 transfer matrices
    vector<vector<pair<int,Mat3>>> adj(Tn+1);

    auto find_idx = [&](const array<int,3>& A, int v)->int{
        if (A[0]==v) return 0;
        if (A[1]==v) return 1;
        if (A[2]==v) return 2;
        return -1; // shouldn't happen
    };

    auto make_transfer = [&](const array<int,3>& A, const array<int,3>& B)->Mat3{
        // A and B share exactly two vertices (the base edge)
        // Build M[i][j] = min( dA(i,u)+dB(u,j) , dA(i,v)+dB(v,j) )
        // where d in one triangle is 0 if same vertex, else 1.
        // Find the two shared vertices
        int shared[2], sc=0;
        for (int x : A) for (int y : B) if (x==y) { shared[sc++]=x; if(sc==2) goto found; }
        found:;
        int Au = find_idx(A, shared[0]);
        int Av = find_idx(A, shared[1]);
        int Bu = find_idx(B, shared[0]);
        int Bv = find_idx(B, shared[1]);

        Mat3 M;
        for (int i=0;i<3;i++){
            for (int j=0;j<3;j++){
                int v1 = triDistIdx(i, Au) + triDistIdx(Bu, j);
                int v2 = triDistIdx(i, Av) + triDistIdx(Bv, j);
                M.a[i][j] = min(v1, v2);
            }
        }
        return M;
    };

    // Read construction (for nodes 4..n), build triangles and clique-tree
    vector<pair<int,int>> base(n+1);
    for (int i=4;i<=n;i++){
        int u,v; cin>>u>>v;
        base[i] = {u,v};
        int tid = i - 2;               // triangle id created at step i
        tri[tid] = {u, i, v};
        uint64_t k = ekey(u,v);
        int prev = last[k];
        // Build transfers in both directions and connect in clique tree
        Mat3 child_to_parent = make_transfer(tri[tid], tri[prev]);
        Mat3 parent_to_child = make_transfer(tri[prev], tri[tid]);
        adj[tid].push_back({prev, child_to_parent});
        adj[prev].push_back({tid, parent_to_child});
        // Update "last" for involved edges
        last[k] = tid;
        last[ekey(u,i)] = tid;
        last[ekey(i,v)] = tid;
    }

    // LCA + lifting matrices
    int LOG = 1;
    while ((1<<LOG) <= Tn) ++LOG;
    vector<int> depth(Tn+1, -1);
    vector<array<int,20>> up(Tn+1); // LOG<=18 for n<=1.5e5; keep 20 for safety
    for (int i=0;i<=Tn;i++) up[i].fill(0);
    // upMat[v][k] is matrix from v to its 2^k-ancestor
    vector<vector<Mat3>> upMat(Tn+1, vector<Mat3>(LOG, Mat3()));
    // BFS from root triangle 1
    queue<int> q;
    depth[1]=0; up[1][0]=1;
    Mat3 I; for (int i=0;i<3;i++) for (int j=0;j<3;j++) I.a[i][j] = (i==j?0:INF);
    for (int j=0;j<LOG;j++) upMat[1][j] = I;
    q.push(1);
    while (!q.empty()){
        int v = q.front(); q.pop();
        for (auto &e : adj[v]){
            int u = e.first;
            if (depth[u] != -1) continue;
            depth[u] = depth[v] + 1;
            up[u][0] = v;
            // We need matrix from u -> parent v. We already have both directions in adj.
            // e is v->u; find u->v:
            Mat3 u_to_v;
            for (auto &bk : adj[u]) if (bk.first == v) { u_to_v = bk.second; break; }
            upMat[u][0] = u_to_v;
            q.push(u);
        }
    }
    for (int j=1;j<LOG;j++){
        for (int v=1; v<=Tn; v++){
            up[v][j] = up[ up[v][j-1] ][j-1];
            upMat[v][j] = minplus_mul( upMat[v][j-1], upMat[ up[v][j-1] ][j-1] );
        }
    }

    auto lca = [&](int a, int b){
        if (depth[a] < depth[b]) swap(a,b);
        int diff = depth[a] - depth[b];
        for (int j=0; j<LOG; j++) if (diff & (1<<j)) a = up[a][j];
        if (a==b) return a;
        for (int j=LOG-1; j>=0; j--){
            if (up[a][j] != up[b][j]) {
                a = up[a][j];
                b = up[b][j];
            }
        }
        return up[a][0];
    };

    auto lift_vec_to_ancestor = [&](array<int,3> v, int node, int anc){
        int cur = node;
        int diff = depth[cur] - depth[anc];
        for (int j=0; j<LOG; j++){
            if (diff & (1<<j)) {
                v = vec_minplus_mul(v, upMat[cur][j]);
                cur = up[cur][j];
            }
        }
        return v;
    };

    auto anchor_triangle = [&](int x)->int{
        return (x <= 3 ? 1 : x - 2);
    };
    auto idx_in_tri = [&](int tid, int v)->int{
        const auto& A = tri[tid];
        if (A[0]==v) return 0;
        if (A[1]==v) return 1;
        if (A[2]==v) return 2;
        return -1;
    };

    int qn; cin>>qn;
    while(qn--){
        int s,t; cin>>s>>t;
        int asid = anchor_triangle(s);
        int atid = anchor_triangle(t);
        int c = lca(asid, atid);

        int is = idx_in_tri(asid, s);
        int it = idx_in_tri(atid, t);
        array<int,3> vs = {1,1,1}; vs[is] = 0;
        array<int,3> vt = {1,1,1}; vt[it] = 0;

        auto vcs = lift_vec_to_ancestor(vs, asid, c);
        auto vct = lift_vec_to_ancestor(vt, atid, c);

        int ans = INF;
        // meet at (possibly different) vertices of LCA triangle
        for (int i=0;i<3;i++){
            for (int j=0;j<3;j++){
                int extra = (i==j ? 0 : 1);
                ans = min(ans, vcs[i] + extra + vct[j]);
            }
        }
        cout << ans << '\n';
    }
    return 0;
}
```

### Flag
```
SEKAI{https://tinyurl.com/nokotan-tree-querying}
```