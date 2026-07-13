pragma Singleton
pragma ComponentBehavior: Bound

import QtQuick
import Quickshell
import Quickshell.Io

// en/ru, persisted in ~/.config/caelestia/binds-ui.json
Singleton {
    id: root

    property string lang: "en"
    readonly property bool isRu: lang === "ru"
    // bump so t() bindings re-eval
    property int rev: 0

    readonly property string configPath: `${Quickshell.env("HOME")}/.config/caelestia/binds-ui.json`

    function t(key: string): string {
        // force binding deps
        root.rev;
        root.lang;
        const pack = root.isRu ? ru : en;
        if (pack[key] !== undefined)
            return pack[key];
        if (en[key] !== undefined)
            return en[key];
        return key;
    }

    function tf(key: string, ...args): string {
        let s = root.t(key);
        for (let i = 0; i < args.length; i++)
            s = s.replace(`%${i + 1}`, String(args[i]));
        return s;
    }

    function setLang(l: string): void {
        if (l !== "en" && l !== "ru")
            return;
        if (lang === l)
            return;
        lang = l;
        rev++;
        save();
    }

    function toggle(): void {
        setLang(isRu ? "en" : "ru");
    }

    function save(): void {
        const body = JSON.stringify({
            lang: root.lang
        });
        storage.setText(body);
    }

    FileView {
        id: storage
        path: root.configPath
        onLoaded: {
            try {
                const data = JSON.parse(text());
                if (data.lang === "ru" || data.lang === "en") {
                    root.lang = data.lang;
                    root.rev++;
                }
            } catch (e) {}
        }
        onLoadFailed: err => {
            // first run — seed default en
            Qt.callLater(() => storage.setText(JSON.stringify({
                lang: root.lang || "en"
            })));
        }
    }

    // English
    readonly property var en: ({
        "nav.all": "All binds",
        "nav.all.desc": "Everything currently active",
        "nav.custom": "Custom",
        "nav.custom.desc": "Your own shortcuts",
        "nav.system": "System",
        "nav.system.desc": "Caelestia / Hyprland defaults",
        "nav.override": "Overrides",
        "nav.override.desc": "System binds you replaced",
        "nav.disabled": "Disabled",
        "nav.disabled.desc": "Temporarily turned off",
        "nav.about": "About",
        "nav.about.desc": "Project, stack, why it exists",
        "nav.author": "Author",
        "nav.author.desc": "Who made this, links, setup",
        "nav.info": "INFO",
        "nav.search": "Search binds",
        "nav.lang": "Language",
        "header.new": "New",
        "header.refresh": "Refresh",
        "header.shown": "%1 shown · %2 total · %3 custom",
        "list.empty": "Nothing here",
        "detail.what": "WHAT IT DOES",
        "detail.technical": "TECHNICAL",
        "detail.meta": "Category · %1    Source · %2",
        "detail.copy": "Copy shortcut",
        "detail.edit": "Edit bind…",
        "detail.override": "Edit / override…",
        "detail.disable": "Disable (temporary)",
        "detail.enable": "Enable",
        "detail.delete": "Delete forever",
        "editor.new": "New bind",
        "editor.edit": "Edit bind",
        "editor.editOverride": "Edit override",
        "editor.override": "Override system bind",
        "editor.keys": "KEYS",
        "editor.keys.ph": "SUPER + B",
        "editor.keys.listening": "Press keys…",
        "editor.capture": "Capture",
        "editor.listening": "Listening…",
        "editor.hint": "Focus the keys field or press Capture, then type a shortcut",
        "editor.hint.listen": "Press a shortcut (Esc cancels)",
        "editor.hint.cancel": "Capture cancelled",
        "editor.hint.stop": "Capture stopped",
        "editor.hint.got": "Captured: %1",
        "editor.action": "ACTION TYPE",
        "editor.cmd": "Command",
        "editor.hypr": "Hypr",
        "editor.global": "Global",
        "editor.caelestia": "Caelestia",
        "editor.payload": "PAYLOAD",
        "editor.title": "TITLE",
        "editor.title.ph": "What it does",
        "editor.desc": "DESCRIPTION",
        "editor.desc.ph": "Longer explanation",
        "editor.category": "CATEGORY",
        "editor.category.ph": "Custom",
        "editor.flags": "FLAGS",
        "editor.cancel": "Cancel",
        "editor.save": "Save",
        "win.title": "Nexus · Keybinds",
        "author.bio": "I build stuff for my own setup. CaelestiaBinds is one of them.",
        "author.setup": "My setup",
        "author.setup.sub": "Hardware and daily driver",
        "author.gpu": "GPU",
        "author.cpu": "CPU",
        "author.ram": "RAM",
        "author.system": "SYSTEM",
        "author.website": "Website",
        "author.website.hint": "Portfolio, projects and other noise. Tap the card to open.",
        "author.tg": "Telegram channel",
        "author.tg.hint": "Updates, builds, breakages and occasional shitposts. Tap to open t.me/rossekdev2",
        "author.open": "Open",
        "author.channel": "channel",
        "project.title": "About CaelestiaBinds",
        "project.tagline": "A visual keybind manager for Hyprland + Caelestia.",
        "project.why.title": "Why it exists",
        "project.why.body": "Editing keybinds from raw lua/json files was painful. I wanted a proper GUI that understands Caelestia, resolves vars.*, and lets me create, override, disable or delete binds without hand-editing configs every time.",
        "project.stack.title": "Stack",
        "project.stack.ui": "UI: Quickshell + Caelestia QML (Nexus-style components, Colours, Tokens)",
        "project.stack.data": "Data: Python CLI (list / save / disable / delete)",
        "project.stack.wm": "WM: Hyprland (lua layout, hypr-user.lua generation)",
        "project.stack.cfg": "Config: ~/.config/caelestia/custom-keybinds.json",
        "project.features.title": "What you can do",
        "project.features.body": "Browse all active binds, search, filter by source, resolve vars.* to real commands, create custom binds, override system ones, disable temporarily, or delete forever.",
        "project.contrib.title": "Contributing",
        "project.contrib.body": "PRs and issues welcome. See CONTRIBUTING.md in the repo for setup, layout and coding notes.",
        "project.repo": "Open on GitHub",
        "project.license": "GPL-3.0 · source in ~/CaelestiaBinds"
    })

    // Russian
    readonly property var ru: ({
        "nav.all": "Все бинды",
        "nav.all.desc": "Всё, что сейчас активно",
        "nav.custom": "Свои",
        "nav.custom.desc": "Ваши шорткаты",
        "nav.system": "Системные",
        "nav.system.desc": "Дефолты Caelestia / Hyprland",
        "nav.override": "Оверрайды",
        "nav.override.desc": "Заменённые системные бинды",
        "nav.disabled": "Выключенные",
        "nav.disabled.desc": "Временно отключены",
        "nav.about": "О проекте",
        "nav.about.desc": "Стек, зачем создан",
        "nav.author": "Автор",
        "nav.author.desc": "Кто сделал, ссылки, сетап",
        "nav.info": "ИНФО",
        "nav.search": "Поиск биндов",
        "nav.lang": "Язык",
        "header.new": "Новый",
        "header.refresh": "Обновить",
        "header.shown": "%1 показано · %2 всего · %3 своих",
        "list.empty": "Пусто",
        "detail.what": "ЧТО ДЕЛАЕТ",
        "detail.technical": "ТЕХНИЧЕСКИ",
        "detail.meta": "Категория · %1    Источник · %2",
        "detail.copy": "Копировать шорткат",
        "detail.edit": "Редактировать…",
        "detail.override": "Оверрайд…",
        "detail.disable": "Отключить (временно)",
        "detail.enable": "Включить",
        "detail.delete": "Удалить навсегда",
        "editor.new": "Новый бинд",
        "editor.edit": "Редактировать бинд",
        "editor.editOverride": "Редактировать оверрайд",
        "editor.override": "Оверрайд системного",
        "editor.keys": "КЛАВИШИ",
        "editor.keys.ph": "SUPER + B",
        "editor.keys.listening": "Жмите клавиши…",
        "editor.capture": "Захват",
        "editor.listening": "Слушаю…",
        "editor.hint": "Фокус на поле клавиш или Захват, затем нажмите шорткат",
        "editor.hint.listen": "Нажмите шорткат (Esc отмена)",
        "editor.hint.cancel": "Захват отменён",
        "editor.hint.stop": "Захват остановлен",
        "editor.hint.got": "Захвачено: %1",
        "editor.action": "ТИП ДЕЙСТВИЯ",
        "editor.cmd": "Команда",
        "editor.hypr": "Hypr",
        "editor.global": "Global",
        "editor.caelestia": "Caelestia",
        "editor.payload": "PAYLOAD",
        "editor.title": "НАЗВАНИЕ",
        "editor.title.ph": "Что делает",
        "editor.desc": "ОПИСАНИЕ",
        "editor.desc.ph": "Подробнее",
        "editor.category": "КАТЕГОРИЯ",
        "editor.category.ph": "Custom",
        "editor.flags": "ФЛАГИ",
        "editor.cancel": "Отмена",
        "editor.save": "Сохранить",
        "win.title": "Nexus · Бинды",
        "author.bio": "Делаю штуки под свой сетап. CaelestiaBinds одна из них.",
        "author.setup": "Мой сетап",
        "author.setup.sub": "Железо и ежедневный драйвер",
        "author.gpu": "GPU",
        "author.cpu": "CPU",
        "author.ram": "ОЗУ",
        "author.system": "СИСТЕМА",
        "author.website": "Сайт",
        "author.website.hint": "Портфолио, проекты и прочий шум. Тап по карточке откроет.",
        "author.tg": "Telegram-канал",
        "author.tg.hint": "Апдейты, сборки, поломки и иногда шитпосты. Тап → t.me/rossekdev2",
        "author.open": "Открыть",
        "author.channel": "канал",
        "project.title": "О CaelestiaBinds",
        "project.tagline": "Визуальный менеджер биндов для Hyprland + Caelestia.",
        "project.why.title": "Зачем",
        "project.why.body": "Править бинды из lua/json-файлов было неудобно. Нужен был нормальный GUI, который понимает Caelestia, резолвит vars.*, и позволяет создавать, оверрайдить, отключать и удалять бинды без ручной правки конфигов каждый раз.",
        "project.stack.title": "Стек",
        "project.stack.ui": "UI: Quickshell + Caelestia QML (компоненты как в Nexus, Colours, Tokens)",
        "project.stack.data": "Данные: Python CLI (list / save / disable / delete)",
        "project.stack.wm": "WM: Hyprland (lua-раскладка, генерация hypr-user.lua)",
        "project.stack.cfg": "Конфиг: ~/.config/caelestia/custom-keybinds.json",
        "project.features.title": "Что умеет",
        "project.features.body": "Просмотр всех активных биндов, поиск, фильтры по источнику, vars.* → реальная команда, свои бинды, оверрайды системных, временное отключение и удаление навсегда.",
        "project.contrib.title": "Контрибьют",
        "project.contrib.body": "PR и issues приветствуются. Смотри CONTRIBUTING.md в репо: setup, структура, заметки по коду.",
        "project.repo": "Открыть на GitHub",
        "project.license": "GPL-3.0 · исходники в ~/CaelestiaBinds"
    })
}
