pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import Caelestia.Config
import Caelestia.Blobs
import qs.components
import qs.components.controls
import qs.services

// Хром как у Nexus. Отступы как в шелле, не трогать.
Item {
    id: root

    property alias backend: backend
    signal closeRequested

    implicitWidth: 1345
    implicitHeight: 845

    property color blobColour: Colours.tPalette.m3surfaceContainerLow
    property int navIndex: 0
    property bool detailOpen: false

    readonly property string pageKey: navPages[navIndex]?.key ?? "all"
    readonly property bool isAbout: pageKey === "about"
    readonly property bool isAuthor: pageKey === "author"
    readonly property bool isInfoPage: isAbout || isAuthor
    readonly property bool showBindsUi: !isInfoPage

    // Метки зависят от языка
    readonly property var navPages: {
        KeybindsI18n.rev;
        return [
            {
                key: "all",
                label: KeybindsI18n.t("nav.all"),
                icon: "keyboard",
                description: KeybindsI18n.t("nav.all.desc")
            },
            {
                key: "custom",
                label: KeybindsI18n.t("nav.custom"),
                icon: "tune",
                description: KeybindsI18n.t("nav.custom.desc")
            },
            {
                key: "system",
                label: KeybindsI18n.t("nav.system"),
                icon: "memory",
                description: KeybindsI18n.t("nav.system.desc")
            },
            {
                key: "override",
                label: KeybindsI18n.t("nav.override"),
                icon: "swap_horiz",
                description: KeybindsI18n.t("nav.override.desc")
            },
            {
                key: "disabled",
                label: KeybindsI18n.t("nav.disabled"),
                icon: "block",
                description: KeybindsI18n.t("nav.disabled.desc")
            },
            {
                key: "about",
                label: KeybindsI18n.t("nav.about"),
                icon: "info",
                description: KeybindsI18n.t("nav.about.desc")
            },
            {
                key: "author",
                label: KeybindsI18n.t("nav.author"),
                icon: "person",
                description: KeybindsI18n.t("nav.author.desc")
            }
        ];
    }

    Behavior on blobColour {
        CAnim {}
    }

    // Помним фильтр биндов, чтобы инфо-вкладки не пересобирали flatModel
    property string lastBindFilter: "all"
    onNavIndexChanged: {
        const k = navPages[navIndex]?.key ?? "all";
        if (k !== "about" && k !== "author")
            lastBindFilter = k;
    }

    KeybindsBackend {
        id: backend
        filter: root.lastBindFilter
    }

    BlobGroup {
        id: blobGroup
        smoothing: Tokens.rounding.medium
        color: root.blobColour
    }

    BlobInvertedRect {
        anchors.fill: parent
        group: blobGroup
        opacity: root.blobColour.a
        radius: Tokens.rounding.large
        borderLeft: navPane.width + navPane.anchors.margins * 2
        borderRight: Tokens.padding.medium
        borderTop: Tokens.padding.medium
        borderBottom: Tokens.padding.medium
    }

    BlobRect {
        id: windowBtnRect
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: Tokens.padding.extraSmall
        group: blobGroup
        opacity: root.blobColour.a
        radius: Tokens.rounding.medium
        implicitWidth: windowBtn.implicitWidth + Tokens.padding.small * 2
        implicitHeight: windowBtn.implicitHeight + Tokens.padding.extraSmall
    }

    IconButton {
        id: windowBtn
        anchors.centerIn: windowBtnRect
        enabled: !editor.open
        icon: "close"
        type: IconButton.Text
        label.fill: 0
        inactiveOnColour: hovered ? Colours.palette.m3error : Colours.palette.m3onSurfaceVariant
        stateLayer.opacity: 0
        onClicked: root.closeRequested()
        label.scale: pressed ? 0.8 : 1
        label.renderType: Text.QtRendering
        Behavior on label.scale {
            Anim {}
        }
    }

    KeybindsNav {
        id: navPane
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.margins: Tokens.padding.large
        width: Math.min(Tokens.sizes.nexus.maxNavWidth, Math.round(root.width / 3))
        enabled: !editor.open
        pages: root.navPages
        currentIndex: root.navIndex
        searchText: backend.search
        onSearchTextChanged: backend.search = navPane.searchText
        onPageSelected: idx => {
            root.navIndex = idx;
            root.detailOpen = false;
            backend.selected = null;
        }
    }

    Connections {
        target: backend
        function onSearchChanged(): void {
            if (navPane.searchText !== backend.search)
                navPane.searchText = backend.search;
        }
    }

    Item {
        id: pageHost
        anchors.left: navPane.right
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.leftMargin: navPane.anchors.margins + Tokens.padding.extraLarge
        anchors.margins: Tokens.padding.extraLarge
        enabled: !editor.open

        ColumnLayout {
            id: header
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            spacing: Tokens.spacing.extraSmall

            RowLayout {
                Layout.fillWidth: true
                Layout.rightMargin: windowBtnRect.width + Tokens.padding.large
                spacing: Tokens.spacing.medium

                IconButton {
                    visible: root.detailOpen
                    icon: "arrow_back"
                    font: Tokens.font.icon.medium
                    type: IconButton.Tonal
                    isRound: true
                    inactiveColour: Colours.tPalette.m3surfaceContainerHigh
                    inactiveOnColour: Colours.palette.m3onSurfaceVariant
                    onClicked: {
                        root.detailOpen = false;
                        backend.selected = null;
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 0

                    StyledText {
                        Layout.fillWidth: true
                        text: root.detailOpen && backend.selected ? backend.selected.title : (root.navPages[root.navIndex]?.label ?? "")
                        font: Tokens.font.title.large
                        elide: Text.ElideRight
                    }

                    StyledText {
                        Layout.fillWidth: true
                        text: root.detailOpen && backend.selected ? backend.selected.keys : (root.navPages[root.navIndex]?.description ?? "")
                        color: Colours.palette.m3onSurfaceVariant
                        font: Tokens.font.body.small
                        elide: Text.ElideRight
                    }
                }

                IconTextButton {
                    visible: !root.detailOpen && root.showBindsUi
                    text: KeybindsI18n.t("header.new")
                    icon: "add"
                    type: TextButton.Filled
                    onClicked: editor.openNew()
                }

                IconTextButton {
                    visible: !root.detailOpen && root.showBindsUi
                    text: KeybindsI18n.t("header.refresh")
                    icon: "refresh"
                    type: TextButton.Tonal
                    Layout.rightMargin: Tokens.padding.small
                    onClicked: backend.reload()
                }
            }

            StyledText {
                visible: !root.detailOpen && root.showBindsUi
                text: KeybindsI18n.tf("header.shown", backend.filteredCount, backend.counts.total, backend.counts.custom)
                color: Colours.palette.m3onSurfaceVariant
                font: Tokens.font.label.small
            }
        }

        Item {
            id: container
            anchors.top: header.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.topMargin: Tokens.padding.large

            KeybindsList {
                id: listView
                anchors.fill: parent
                visible: true
                opacity: root.showBindsUi && !root.detailOpen ? 1 : 0
                enabled: root.showBindsUi && !root.detailOpen
                z: 1
                backend: backend
                onBindActivated: b => {
                    backend.selected = b;
                    root.detailOpen = true;
                }
            }

            KeybindsDetail {
                id: detailView
                anchors.fill: parent
                visible: true
                opacity: root.showBindsUi && root.detailOpen ? 1 : 0
                enabled: root.showBindsUi && root.detailOpen
                z: 2
                backend: backend
                onBack: {
                    root.detailOpen = false;
                    backend.selected = null;
                }
                onEditRequested: b => editor.openEdit(b, b.source === "system")
            }

            // About: про проект
            KeybindsProject {
                id: projectView
                anchors.fill: parent
                visible: true
                opacity: root.isAbout ? 1 : 0
                enabled: root.isAbout
                z: root.isAbout ? 3 : 0
            }

            // Author: ник, ава, ссылки, сетап
            KeybindsAbout {
                id: authorView
                anchors.fill: parent
                visible: true
                opacity: root.isAuthor ? 1 : 0
                enabled: root.isAuthor
                z: root.isAuthor ? 3 : 0
            }
        }
    }

    KeybindsEditor {
        id: editor
        anchors.fill: parent
        backend: backend
    }
}
