// All of the Node.js APIs are available in the preload process.
// It has the same sandbox as a Chrome extension.

const path = require('path')
const url = require('url')
const { Titlebar, Color } = require('custom-electron-titlebar');
const { Menu } = require('electron').remote

window.addEventListener('DOMContentLoaded', () => {

    let titlebar = new Titlebar({
        backgroundColor: Color.fromHex('#222222'),
        menu: new Menu(),
        icon: url.format(path.join(__dirname, '/icon.png')),
    });

    titlebar.setHorizontalAlignment('left');

    const replaceText = (selector, text) => {
        const element = document.getElementById(selector)
        if (element) element.innerText = text
    }

    for (const type of ['chrome', 'node', 'electron']) {
        replaceText(`${type}-version`, process.versions[type])
    }
})
