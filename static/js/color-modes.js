/*!
 * Color mode toggler for Bootstrap's docs (https://getbootstrap.com/)
 * Copyright 2011-2024 The Bootstrap Authors
 * Licensed under the Creative Commons Attribution 3.0 Unported License.
 */

(() => {
  'use strict'

  // Remove getStoredTheme and getPreferredTheme functions as they are no longer needed
  // const getStoredTheme = () => localStorage.getItem('theme')
  // const setStoredTheme = theme => localStorage.setItem('theme', theme)

  // const getPreferredTheme = () => {
  //   const storedTheme = getStoredTheme()
  //   if (storedTheme) {
  //     return storedTheme
  //   }

  //   return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  // }

  const setTheme = theme => {
    document.documentElement.setAttribute('data-bs-theme', theme)
  }

  // Set the theme to 'dark' explicitly
  setTheme('dark')

  const showActiveTheme = (theme, focus = false) => {
    const themeSwitcher = document.querySelector('#bd-theme')

    if (!themeSwitcher) {
      return
    }

    const themeSwitcherText = document.querySelector('#bd-theme-text')
    const activeThemeIcon = document.querySelector('.theme-icon-active use')
    const btnToActive = document.querySelector(`[data-bs-theme-value="${theme}"]`)
    const svgOfActiveBtn = btnToActive.querySelector('svg use').getAttribute('href')

    document.querySelectorAll('[data-bs-theme-value]').forEach(element => {
      element.classList.remove('active')
      element.setAttribute('aria-pressed', 'false')
    })

    btnToActive.classList.add('active')
    btnToActive.setAttribute('aria-pressed', 'true')
    activeThemeIcon.setAttribute('href', svgOfActiveBtn)
    const themeSwitcherLabel = `${themeSwitcherText.textContent} (${btnToActive.dataset.bsThemeValue})`
    themeSwitcher.setAttribute('aria-label', themeSwitcherLabel)

    if (focus) {
      themeSwitcher.focus()
    }
  }

  // Remove the event listener for system preference change
  // window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
  //   const storedTheme = getStoredTheme()
  //   if (storedTheme !== 'light' && storedTheme !== 'dark') {
  //     setTheme(getPreferredTheme())
  //   }
  // })

  window.addEventListener('DOMContentLoaded', () => {
    showActiveTheme('dark') // Show active theme as 'dark' by default

    document.querySelectorAll('[data-bs-theme-value]')
      .forEach(toggle => {
        toggle.addEventListener('click', () => {
          const theme = toggle.getAttribute('data-bs-theme-value')
          // setStoredTheme(theme) // No need to store the theme
          setTheme(theme)
          showActiveTheme(theme, true)
        })
      })
  })
})()
