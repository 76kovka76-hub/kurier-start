(() => {
  "use strict";
  const STORAGE_KEY = "kurierStartCity";
  const clean = (value) => String(value || "").replace(/[<>]/g, "").trim().slice(0, 70);
  const getSaved = () => { try { return clean(localStorage.getItem(STORAGE_KEY)); } catch (_) { return ""; } };
  const save = (value) => { try { localStorage.setItem(STORAGE_KEY, value); } catch (_) {} };
  const updateCity = (city, source) => {
    city = clean(city);
    if (!city) return;
    const localCard = document.querySelector(".city-personal");
    if (localCard) localCard.hidden = false;
    const value = document.getElementById("visitor-city");
    if (value) value.textContent = city;
    const note = document.getElementById("city-note");
    if (note) note.textContent = source === "manual" ? "Город выбран вами" : "Город определён приблизительно по IP";
    const localTitle = document.getElementById("city-personal-title");
    if (localTitle) localTitle.textContent = "Информация для " + city;
    const localText = document.getElementById("city-personal-text");
    if (localText) localText.textContent = "Проверьте, доступен ли набор курьеров в " + city + ", и уточните актуальные требования, график и выплаты до начала работы. Наличие вакансий и условия могут отличаться даже внутри одного региона.";
    document.querySelectorAll("[data-city-text]").forEach((node) => { node.textContent = city; });
    document.querySelectorAll('a[href*="wa.me/79201461682"]').forEach((link) => {
      const message = "Здравствуйте! Я из города " + city + ". Подскажите, пожалуйста, актуальные условия и наличие набора курьеров.";
      link.href = "https://wa.me/79201461682?text=" + encodeURIComponent(message);
    });
  };
  const start = async () => {
    const main = document.querySelector("main");
    if (!main) return;
    const bar = document.createElement("section");
    bar.className = "city-bar";
    bar.setAttribute("aria-label", "Ваш город");
    bar.innerHTML = '<div class="city-bar-copy"><span class="city-bar-label">ВАШ ГОРОД</span><strong id="visitor-city" aria-live="polite" aria-atomic="true">Город не выбран</strong><small id="city-note">При желании укажите его вручную</small></div><button type="button" class="city-change" id="city-change" aria-expanded="false" aria-controls="city-edit">Изменить город</button><form class="city-edit" id="city-edit" aria-label="Выбор города" hidden><label for="city-input">Укажите город</label><input id="city-input" name="city" maxlength="70" placeholder="Например, Казань" required><button type="submit">Сохранить</button></form>';
    const header = document.querySelector(".site-header");
    if (header) header.insertAdjacentElement("afterend", bar);
    else main.insertAdjacentElement("beforebegin", bar);
    const localCard = document.createElement("aside");
    localCard.className = "city-personal";
    localCard.hidden = true;
    localCard.innerHTML = '<strong id="city-personal-title" aria-live="polite" aria-atomic="true">Информация для вашего города</strong><p id="city-personal-text">Уточняем региональные условия. Можно изменить город вручную.</p><a href="https://vkusvill.ru/job/courier/" target="_blank" rel="noopener noreferrer">Проверить официальные вакансии ↗</a>';
    bar.insertAdjacentElement("afterend", localCard);
    const edit = document.getElementById("city-edit");
    const changeButton = document.getElementById("city-change");
    const cityInput = document.getElementById("city-input");
    changeButton.addEventListener("click", () => {
      edit.hidden = !edit.hidden;
      changeButton.setAttribute("aria-expanded", String(!edit.hidden));
      if (!edit.hidden) cityInput.focus();
    });
    edit.addEventListener("submit", (event) => {
      event.preventDefault();
      const city = clean(document.getElementById("city-input").value);
      if (!city) return;
      save(city);
      updateCity(city, "manual");
      edit.hidden = true;
      changeButton.setAttribute("aria-expanded", "false");
      changeButton.focus();
    });
    const saved = getSaved();
    if (saved) { updateCity(saved, "manual"); return; }
    try {
      const response = await fetch("https://ipapi.co/json/", { headers: { Accept: "application/json" }, cache: "no-store" });
      if (!response.ok) throw new Error("Geolocation unavailable");
      const data = await response.json();
      const city = clean(data.city), region = clean(data.region), country = clean(data.country_name);
      const detected = [city, region && region !== city ? region : "", country].filter(Boolean).join(", ");
      if (detected) { save(detected); updateCity(detected, "ip"); }
      else { document.getElementById("visitor-city").textContent = "Город не выбран"; }
    } catch (_) { document.getElementById("visitor-city").textContent = "Город не выбран"; }
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, { once: true });
  else start();
})();