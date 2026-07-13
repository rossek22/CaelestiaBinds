pragma ComponentBehavior: Bound

import QtQuick
import Quickshell
import Quickshell.Io

Item {
    id: root

    // set by install.sh / launcher, fallback ~/CaelestiaBinds
    readonly property string rootDir: {
        const e = Quickshell.env("CAELESTIA_BINDS_ROOT");
        if (e && e.length)
            return e;
        return `${Quickshell.env("HOME")}/CaelestiaBinds`;
    }
    readonly property string cli: `${rootDir}/python/cli.py`

    property var binds: []
    property var counts: ({
        total: 0,
        custom: 0,
        system: 0,
        override: 0,
        disabled: 0
    })
    property bool loading: false
    property string filter: "all"
    property string search: ""
    property var selected: null
    property bool showResolved: true
    property var flatModel: []
    property int filteredCount: 0

    function matchesFilter(b): bool {
        if (root.filter === "custom" && b.source !== "custom")
            return false;
        if (root.filter === "system" && b.source !== "system")
            return false;
        if (root.filter === "override" && b.source !== "override")
            return false;
        if (root.filter === "disabled" && b.enabled)
            return false;
        const q = root.search.trim().toLowerCase();
        if (!q)
            return true;
        const blob = `${b.keys} ${b.title} ${b.detail} ${b.category} ${b.technical} ${b.technicalResolved} ${b.source}`.toLowerCase();
        return blob.includes(q);
    }

    function rebuildFlat(): void {
        const groups = {};
        const order = [];
        let n = 0;
        for (let i = 0; i < root.binds.length; i++) {
            const b = root.binds[i];
            if (!matchesFilter(b))
                continue;
            n++;
            const c = b.category || "General";
            if (!groups[c]) {
                groups[c] = [];
                order.push(c);
            }
            groups[c].push(b);
        }
        const out = [];
        for (let gi = 0; gi < order.length; gi++) {
            const cat = order[gi];
            const items = groups[cat];
            out.push({
                kind: "header",
                id: `h:${cat}`,
                title: cat
            });
            for (let i = 0; i < items.length; i++) {
                const b = items[i];
                out.push({
                    kind: "row",
                    id: b.id,
                    bind: b,
                    first: i === 0,
                    last: i === items.length - 1,
                    only: items.length === 1
                });
            }
        }
        root.filteredCount = n;
        root.flatModel = out;
    }

    onBindsChanged: rebuildFlat()
    onFilterChanged: rebuildFlat()
    onSearchChanged: rebuildFlat()

    function reload(): void {
        root.loading = true;
        listProc.running = false;
        listProc.running = true;
    }

    function deleteBind(id: string): void {
        actionProc.command = ["python3", root.cli, "delete", id];
        actionProc.running = true;
    }

    function disableBind(id: string): void {
        actionProc.command = ["python3", root.cli, "disable", id];
        actionProc.running = true;
    }

    function enableBind(id: string): void {
        actionProc.command = ["python3", root.cli, "enable", id];
        actionProc.running = true;
    }

    function saveBind(obj): void {
        // tiny payload, fine as argv
        saveProc.command = ["python3", root.cli, "save-json", JSON.stringify(obj)];
        saveProc.running = false;
        saveProc.running = true;
    }

    function applyPayload(jsonText: string): void {
        try {
            const data = JSON.parse(jsonText);
            if (data.binds)
                root.binds = data.binds;
            if (data.counts)
                root.counts = data.counts;
            if (root.selected) {
                const id = root.selected.id;
                root.selected = root.binds.find(b => b.id === id) ?? null;
            }
        } catch (e) {
            console.error("keybinds parse error", e, jsonText.slice(0, 200));
        }
        root.loading = false;
        rebuildFlat();
    }

    Component.onCompleted: reload()

    Process {
        id: listProc
        command: ["python3", root.cli, "list"]
        stdout: StdioCollector {
            onStreamFinished: root.applyPayload(text)
        }
    }

    Process {
        id: actionProc
        stdout: StdioCollector {
            onStreamFinished: root.applyPayload(text)
        }
    }

    Process {
        id: saveProc
        // stdin wired at runtime
        stdout: StdioCollector {
            onStreamFinished: root.applyPayload(text)
        }
    }
}
