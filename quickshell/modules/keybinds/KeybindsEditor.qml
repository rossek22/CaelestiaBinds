pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import Quickshell
import Caelestia.Config
import qs.components
import qs.components.containers
import qs.components.controls
import qs.services

// Редактор бинда: полноэкранная модалка, анимация, блокировка фона, захват клавиш
Item {
    id: root

    required property var backend
    property var bind: null
    property bool asOverride: false
    property bool open: false
    property string kind: "exec"
    property bool capturing: false

    // Визуальное состояние для анимации (open может закрыться после fade-out)
    property real scrimOpacity: 0
    property real cardOpacity: 0
    property real cardScale: 0.92
    property real cardY: 18

    signal closed
    signal saved

    anchors.fill: parent
    z: 1000
    // Держим в дереве пока анимируемся
    visible: open || scrimOpacity > 0.001
    // Блокируем клики/колёсико сквозь модалку
    enabled: visible

    // Сплошные цвета: palette может быть полупрозрачной из-за transparency
    readonly property color solidSurface: {
        const c = Colours.palette.m3surface;
        return Qt.rgba(c.r, c.g, c.b, 1);
    }
    readonly property color solidContainer: {
        const c = Colours.palette.m3surfaceContainerHigh;
        return Qt.rgba(c.r, c.g, c.b, 1);
    }
    readonly property color solidScrim: Qt.rgba(0, 0, 0, 0.82)

    readonly property string modeTitle: {
        if (asOverride || bind?.source === "system")
            return KeybindsI18n.t("editor.override");
        if (bind?.source === "override")
            return KeybindsI18n.t("editor.editOverride");
        if (bind)
            return KeybindsI18n.t("editor.edit");
        return KeybindsI18n.t("editor.new");
    }

    function openNew(): void {
        bind = null;
        asOverride = false;
        kind = "exec";
        capturing = false;
        keysField.text = "";
        payloadField.text = "";
        titleField.text = "";
        detailField.text = "";
        catField.text = "Custom";
        flagLocked.checked = false;
        flagRepeat.checked = false;
        flagRelease.checked = false;
        open = true;
        captureHint.text = KeybindsI18n.t("editor.hint");
        playOpen();
    }

    function openEdit(b, overrideMode = false): void {
        bind = b;
        asOverride = overrideMode || b?.source === "system";
        capturing = false;
        if (b?.kind && b.kind !== "system")
            kind = b.kind;
        else if ((b?.technical || "").startsWith("global "))
            kind = "global";
        else if ((b?.technical || "").includes("hyprctl dispatch"))
            kind = "hypr";
        else
            kind = "exec";

        keysField.text = b?.keysRaw || b?.keys || "";
        if (b?.payload)
            payloadField.text = b.payload;
        else {
            const t = b?.technical || "";
            if (t.startsWith("exec vars."))
                payloadField.text = t.slice(5);
            else if (t.startsWith("exec "))
                payloadField.text = t.slice(5);
            else if (t.startsWith("global "))
                payloadField.text = t.slice(7);
            else if (t.startsWith("hyprctl dispatch "))
                payloadField.text = t.slice(17);
            else
                payloadField.text = t;
        }
        titleField.text = (b?.title || "").replace("[disabled] ", "");
        detailField.text = b?.detail || "";
        catField.text = b?.category && b.category !== "General" ? b.category : "Custom";
        const flags = b?.flags || [];
        flagLocked.checked = flags.indexOf("locked") >= 0;
        flagRepeat.checked = flags.indexOf("repeating") >= 0;
        flagRelease.checked = flags.indexOf("release") >= 0;
        open = true;
        captureHint.text = KeybindsI18n.t("editor.hint");
        playOpen();
    }

    function playOpen(): void {
        closeAnim.stop();
        // Старт с «закрытого» кадра, чтобы анимка всегда видна
        scrimOpacity = 0;
        cardOpacity = 0;
        cardScale = 0.92;
        cardY = 18;
        openAnim.start();
        forceActiveFocus();
    }

    function close(): void {
        if (!open && scrimOpacity <= 0)
            return;
        capturing = false;
        // Уже закрываемся
        if (closeAnim.running)
            return;
        openAnim.stop();
        closeAnim.start();
    }

    function finishClose(): void {
        open = false;
        scrimOpacity = 0;
        cardOpacity = 0;
        cardScale = 0.92;
        cardY = 18;
        closed();
    }

    function save(): void {
        const flags = [];
        if (flagLocked.checked)
            flags.push("locked");
        if (flagRepeat.checked)
            flags.push("repeating");
        if (flagRelease.checked)
            flags.push("release");

        const payload = {
            id: root.bind?.id || "",
            keys: keysField.text.trim(),
            kind: root.kind,
            payload: payloadField.text.trim(),
            title: titleField.text.trim(),
            detail: detailField.text.trim(),
            category: catField.text.trim() || "Custom",
            flags: flags,
            enabled: true,
            mode: (root.asOverride || root.bind?.source === "system") ? "override" : "custom",
            baseKeys: root.bind?.keysRaw || root.bind?.keys || keysField.text.trim(),
            previousKeys: root.bind?.keysRaw || root.bind?.keys || "",
            asOverride: root.asOverride || root.bind?.source === "system"
        };
        if (!payload.keys || !payload.payload)
            return;
        root.backend.saveBind(payload);
        root.close();
        root.saved();
    }

    function keyName(event): string {
        const k = event.key;
        const map = {
            [Qt.Key_Return]: "Return",
            [Qt.Key_Enter]: "Return",
            [Qt.Key_Escape]: "Escape",
            [Qt.Key_Space]: "Space",
            [Qt.Key_Tab]: "Tab",
            [Qt.Key_Backspace]: "BackSpace",
            [Qt.Key_Delete]: "Delete",
            [Qt.Key_Insert]: "Insert",
            [Qt.Key_Home]: "Home",
            [Qt.Key_End]: "End",
            [Qt.Key_PageUp]: "Page_Up",
            [Qt.Key_PageDown]: "Page_Down",
            [Qt.Key_Left]: "Left",
            [Qt.Key_Right]: "Right",
            [Qt.Key_Up]: "Up",
            [Qt.Key_Down]: "Down",
            [Qt.Key_Print]: "Print",
            [Qt.Key_Minus]: "minus",
            [Qt.Key_Equal]: "equal",
            [Qt.Key_Comma]: "comma",
            [Qt.Key_Period]: "period",
            [Qt.Key_Slash]: "slash",
            [Qt.Key_Backslash]: "backslash",
            [Qt.Key_Semicolon]: "semicolon",
            [Qt.Key_Apostrophe]: "apostrophe",
            [Qt.Key_BracketLeft]: "bracketleft",
            [Qt.Key_BracketRight]: "bracketright",
            [Qt.Key_QuoteLeft]: "grave"
        };
        if (map[k])
            return map[k];
        if (k >= Qt.Key_F1 && k <= Qt.Key_F12)
            return `F${k - Qt.Key_F1 + 1}`;
        if (k >= Qt.Key_0 && k <= Qt.Key_9)
            return String.fromCharCode(k);
        if (k >= Qt.Key_A && k <= Qt.Key_Z)
            return String.fromCharCode(k);
        if (event.text && event.text.length === 1 && event.text.charCodeAt(0) >= 33)
            return event.text.toUpperCase();
        return "";
    }

    function isModifier(key: int): bool {
        return key === Qt.Key_Shift || key === Qt.Key_Control || key === Qt.Key_Alt || key === Qt.Key_Meta || key === Qt.Key_Super_L || key === Qt.Key_Super_R || key === Qt.Key_AltGr || key === Qt.Key_CapsLock || key === Qt.Key_NumLock || key === Qt.Key_ScrollLock;
    }

    function handleCapture(event): bool {
        if (!root.capturing)
            return false;
        if (isModifier(event.key)) {
            event.accepted = true;
            return true;
        }
        if (event.key === Qt.Key_Escape) {
            root.capturing = false;
            captureHint.text = KeybindsI18n.t("editor.hint.cancel");
            event.accepted = true;
            return true;
        }

        const parts = [];
        // Super часто приходит как Meta на X11/Wayland
        if (event.modifiers & Qt.MetaModifier)
            parts.push("SUPER");
        if (event.modifiers & Qt.ControlModifier)
            parts.push("CTRL");
        if (event.modifiers & Qt.AltModifier)
            parts.push("ALT");
        if (event.modifiers & Qt.ShiftModifier)
            parts.push("SHIFT");

        const name = root.keyName(event);
        if (!name || name === "Escape") {
            event.accepted = true;
            return true;
        }
        parts.push(name);
        keysField.text = parts.join(" + ");
        root.capturing = false;
        captureHint.text = KeybindsI18n.tf("editor.hint.got", keysField.text);
        // Поле остаётся в фокусе для повторного захвата; Esc → ручной ввод
        event.accepted = true;
        return true;
    }

    onCapturingChanged: {
        if (capturing) {
            keysField.forceActiveFocus();
            captureHint.text = KeybindsI18n.t("editor.hint.listen");
        }
    }



    // Глобальный захват клавиш пока open
    Keys.enabled: open
    Keys.priority: Keys.BeforeItem
    Keys.onPressed: event => {
        if (handleCapture(event))
            return;
        // Esc закрывает модалку, если не в capture
        if (event.key === Qt.Key_Escape && open) {
            root.close();
            event.accepted = true;
        }
    }

    // Затемнение + блокер на всё окно (nav + контент)
    Rectangle {
        id: scrim
        anchors.fill: parent
        z: 0
        color: root.solidScrim
        opacity: root.scrimOpacity

        // Ест клики/колёсико: фон не скроллится и не кликается
        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            preventStealing: true
            acceptedButtons: Qt.AllButtons
            onPressed: mouse => {
                mouse.accepted = true;
            }
            onClicked: {
                if (root.capturing) {
                    root.capturing = false;
                    captureHint.text = KeybindsI18n.t("editor.hint.cancel");
                } else {
                    root.close();
                }
            }
            onWheel: wheel => {
                wheel.accepted = true;
            }
        }
    }

    // Непрозрачная карточка диалога
    Rectangle {
        id: card
        z: 1
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        anchors.verticalCenterOffset: root.cardY
        width: Math.min(parent.width - 48, 520)
        height: Math.min(parent.height - 48, Math.max(420, parent.height * 0.88))
        radius: Tokens.rounding.extraLarge
        color: root.solidSurface
        border.color: Colours.palette.m3outlineVariant
        border.width: 1
        clip: true
        opacity: root.cardOpacity
        scale: root.cardScale
        transformOrigin: Item.Center

        // Доп. заливка на случай альфы у детей
        Rectangle {
            anchors.fill: parent
            radius: parent.radius
            color: root.solidSurface
            z: -1
        }

        // Не даём wheel «пробить» карточку к списку под модалкой
        MouseArea {
            anchors.fill: parent
            z: -1
            acceptedButtons: Qt.NoButton
            onWheel: wheel => {
                wheel.accepted = true;
            }
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Tokens.padding.extraLarge
            spacing: Tokens.spacing.medium

            RowLayout {
                Layout.fillWidth: true
                StyledText {
                    Layout.fillWidth: true
                    text: root.modeTitle
                    font: Tokens.font.title.medium
                    color: Colours.palette.m3onSurface
                }
                IconButton {
                    icon: "close"
                    type: IconButton.Text
                    onClicked: root.close()
                }
            }

            Flickable {
                id: flick
                Layout.fillWidth: true
                Layout.fillHeight: true
                contentHeight: form.implicitHeight
                clip: true
                boundsBehavior: Flickable.StopAtBounds
                flickableDirection: Flickable.VerticalFlick

                ColumnLayout {
                    id: form
                    width: flick.width
                    spacing: Tokens.spacing.medium

                    StyledText {
                        text: KeybindsI18n.t("editor.keys")
                        color: Colours.palette.m3onSurfaceVariant
                        font: Tokens.font.label.medium
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: keysRow.implicitHeight + Tokens.padding.small * 2
                        radius: Tokens.rounding.large
                        color: root.solidContainer
                        border.color: root.capturing ? Colours.palette.m3primary : Colours.palette.m3outlineVariant
                        border.width: root.capturing ? 2 : 1

                        RowLayout {
                            id: keysRow
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.leftMargin: Tokens.padding.medium
                            anchors.rightMargin: Tokens.padding.small
                            spacing: Tokens.spacing.small

                            TextField {
                                id: keysField
                                Layout.fillWidth: true
                                placeholderText: root.capturing ? KeybindsI18n.t("editor.keys.listening") : KeybindsI18n.t("editor.keys.ph")
                                color: Colours.palette.m3onSurface
                                placeholderTextColor: Colours.palette.m3outline
                                font: Tokens.font.body.medium
                                background: null
                                // Режим захвата подменяет ввод на аккорд
                                readOnly: root.capturing
                                selectByMouse: !root.capturing

                                // Фокус на KEYS включает захват (Esc отменяет, дальше обычный ввод)
                                onActiveFocusChanged: {
                                    if (activeFocus)
                                        root.capturing = true;
                                    else if (root.capturing)
                                        root.capturing = false;
                                }

                                Keys.priority: Keys.BeforeItem
                                Keys.onPressed: event => {
                                    if (root.handleCapture(event))
                                        return;
                                }
                            }

                            IconTextButton {
                                id: captureBtn
                                text: root.capturing ? KeybindsI18n.t("editor.listening") : KeybindsI18n.t("editor.capture")
                                icon: root.capturing ? "keyboard" : "keyboard_keys"
                                type: root.capturing ? TextButton.Filled : TextButton.Tonal
                                onClicked: {
                                    root.capturing = !root.capturing;
                                    if (root.capturing) {
                                        keysField.forceActiveFocus();
                                        captureHint.text = KeybindsI18n.t("editor.hint.listen");
                                    } else {
                                        captureHint.text = KeybindsI18n.t("editor.hint.stop");
                                    }
                                }
                            }
                        }
                    }

                    StyledText {
                        id: captureHint
                        Layout.fillWidth: true
                        text: KeybindsI18n.t("editor.hint")
                        color: root.capturing ? Colours.palette.m3primary : Colours.palette.m3outline
                        font: Tokens.font.label.small
                        wrapMode: Text.Wrap
                    }

                    StyledText {
                        text: KeybindsI18n.t("editor.action")
                        color: Colours.palette.m3onSurfaceVariant
                        font: Tokens.font.label.medium
                    }

                    Flow {
                        Layout.fillWidth: true
                        spacing: Tokens.spacing.small
                        Repeater {
                            model: {
                                KeybindsI18n.rev;
                                return [
                                    {
                                        k: "exec",
                                        t: KeybindsI18n.t("editor.cmd")
                                    },
                                    {
                                        k: "hypr",
                                        t: KeybindsI18n.t("editor.hypr")
                                    },
                                    {
                                        k: "global",
                                        t: KeybindsI18n.t("editor.global")
                                    },
                                    {
                                        k: "caelestia",
                                        t: KeybindsI18n.t("editor.caelestia")
                                    }
                                ];
                            }
                            IconTextButton {
                                required property var modelData
                                text: modelData.t
                                type: root.kind === modelData.k ? TextButton.Filled : TextButton.Tonal
                                onClicked: root.kind = modelData.k
                            }
                        }
                    }

                    StyledText {
                        text: KeybindsI18n.t("editor.payload")
                        color: Colours.palette.m3onSurfaceVariant
                        font: Tokens.font.label.medium
                    }
                    Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: payloadField.implicitHeight + Tokens.padding.medium
                        radius: Tokens.rounding.large
                        color: root.solidContainer
                        TextField {
                            id: payloadField
                            anchors.fill: parent
                            anchors.margins: Tokens.padding.small
                            placeholderText: root.kind === "hypr" ? "killactive" : root.kind === "global" ? "caelestia:launcher" : "foot"
                            color: Colours.palette.m3onSurface
                            placeholderTextColor: Colours.palette.m3outline
                            font: Tokens.font.body.medium
                            background: null
                        }
                    }

                    StyledText {
                        text: KeybindsI18n.t("editor.title")
                        color: Colours.palette.m3onSurfaceVariant
                        font: Tokens.font.label.medium
                    }
                    Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: titleField.implicitHeight + Tokens.padding.medium
                        radius: Tokens.rounding.large
                        color: root.solidContainer
                        TextField {
                            id: titleField
                            anchors.fill: parent
                            anchors.margins: Tokens.padding.small
                            placeholderText: KeybindsI18n.t("editor.title.ph")
                            color: Colours.palette.m3onSurface
                            placeholderTextColor: Colours.palette.m3outline
                            font: Tokens.font.body.medium
                            background: null
                        }
                    }

                    StyledText {
                        text: KeybindsI18n.t("editor.desc")
                        color: Colours.palette.m3onSurfaceVariant
                        font: Tokens.font.label.medium
                    }
                    Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: detailField.implicitHeight + Tokens.padding.medium
                        radius: Tokens.rounding.large
                        color: root.solidContainer
                        TextField {
                            id: detailField
                            anchors.fill: parent
                            anchors.margins: Tokens.padding.small
                            placeholderText: KeybindsI18n.t("editor.desc.ph")
                            color: Colours.palette.m3onSurface
                            placeholderTextColor: Colours.palette.m3outline
                            font: Tokens.font.body.medium
                            background: null
                        }
                    }

                    StyledText {
                        text: KeybindsI18n.t("editor.category")
                        color: Colours.palette.m3onSurfaceVariant
                        font: Tokens.font.label.medium
                    }
                    Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: catField.implicitHeight + Tokens.padding.medium
                        radius: Tokens.rounding.large
                        color: root.solidContainer
                        TextField {
                            id: catField
                            anchors.fill: parent
                            anchors.margins: Tokens.padding.small
                            placeholderText: KeybindsI18n.t("editor.category.ph")
                            color: Colours.palette.m3onSurface
                            placeholderTextColor: Colours.palette.m3outline
                            font: Tokens.font.body.medium
                            background: null
                        }
                    }

                    RowLayout {
                        spacing: Tokens.spacing.small
                        StyledText {
                            text: KeybindsI18n.t("editor.flags")
                            color: Colours.palette.m3onSurfaceVariant
                            font: Tokens.font.label.medium
                        }
                        IconTextButton {
                            id: flagLocked
                            text: "locked"
                            isToggle: true
                            type: checked ? TextButton.Filled : TextButton.Tonal
                            onClicked: checked = !checked
                        }
                        IconTextButton {
                            id: flagRepeat
                            text: "repeating"
                            isToggle: true
                            type: checked ? TextButton.Filled : TextButton.Tonal
                            onClicked: checked = !checked
                        }
                        IconTextButton {
                            id: flagRelease
                            text: "release"
                            isToggle: true
                            type: checked ? TextButton.Filled : TextButton.Tonal
                            onClicked: checked = !checked
                        }
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignRight
                spacing: Tokens.spacing.small
                IconTextButton {
                    text: KeybindsI18n.t("editor.cancel")
                    icon: "close"
                    type: TextButton.Tonal
                    onClicked: root.close()
                }
                IconTextButton {
                    text: KeybindsI18n.t("editor.save")
                    icon: "check"
                    type: TextButton.Filled
                    onClicked: root.save()
                }
            }
        }
    }

    // Анимация открытия: scrim fade + card scale/fade/slide
    ParallelAnimation {
        id: openAnim
        NumberAnimation {
            target: root
            property: "scrimOpacity"
            to: 1
            duration: 220
            easing.type: Easing.OutCubic
        }
        NumberAnimation {
            target: root
            property: "cardOpacity"
            to: 1
            duration: 240
            easing.type: Easing.OutCubic
        }
        NumberAnimation {
            target: root
            property: "cardScale"
            to: 1
            duration: 280
            easing.type: Easing.OutBack
            easing.overshoot: 1.15
        }
        NumberAnimation {
            target: root
            property: "cardY"
            to: 0
            duration: 280
            easing.type: Easing.OutCubic
        }
    }

    ParallelAnimation {
        id: closeAnim
        NumberAnimation {
            target: root
            property: "scrimOpacity"
            to: 0
            duration: 160
            easing.type: Easing.InCubic
        }
        NumberAnimation {
            target: root
            property: "cardOpacity"
            to: 0
            duration: 140
            easing.type: Easing.InCubic
        }
        NumberAnimation {
            target: root
            property: "cardScale"
            to: 0.94
            duration: 160
            easing.type: Easing.InCubic
        }
        NumberAnimation {
            target: root
            property: "cardY"
            to: 12
            duration: 160
            easing.type: Easing.InCubic
        }
        onFinished: root.finishClose()
    }
}
