"use strict";

const URL_REGEX = /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([\/\w .-]*)*\/?$/

function msbShareButtonAction(target) {
  if (msbConfig && msbConfig.openModal && msbConfig.addressFieldSelector) {
    if (document.querySelector(msbConfig.buttonModalSelector)) {
      let bms = document.querySelector(msbConfig.buttonModalSelector)
      bms.data = { target }
      bms.addEventListener('click', () => msbOnShare(), false)
    }
    msbConfig.openModal(target)
  }
}

function msbOnShare(_target) {
  if (msbConfig && msbConfig.addressFieldSelector && msbConfig.buttonModalSelector) {
    let target = !!_target ? _target : document.querySelector(msbConfig.buttonModalSelector).data.target
    let msbInstanceAddress = document.querySelector(`${msbConfig.addressFieldSelector}`).value

    if (msbInstanceAddress.match(URL_REGEX)) {
      window.open(`${msbInstanceAddress}/share?text=${target}`, `__blank`)
      if (msbConfig && msbConfig.openModal && msbConfig.closeModal) {
        msbConfig.closeModal()
      }
    }
  }
}

(function() {

  let msbButtons = document.querySelectorAll('.mastodon-share-button')

  for(let i = 0; i < msbButtons.length; i++) {
    (function(j) {

      let msbTarget = msbButtons[j].dataset.target

      /**
       * Set the listener in each button
       */
      msbButtons[j].addEventListener('click', () => { msbShareButtonAction(msbTarget) }, true)

    })(i)
  }

})()