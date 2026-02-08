(() => {
  const slider = document.getElementById('slider');
  if (!slider) return;
  const slides = Array.from(slider.querySelectorAll('.slide'));
  const prev = slider.querySelector('.prev');
  const next = slider.querySelector('.next');
  const dotsWrap = document.getElementById('dots');

  let index = 0;
  const setActive = (i) => {
    slides.forEach((s, k) => s.classList.toggle('active', k === i));
    if (dotsWrap) Array.from(dotsWrap.children).forEach((d, k) => d.classList.toggle('active', k === i));
  };

  // Dots
  slides.forEach((_, i) => {
    const b = document.createElement('button');
    b.addEventListener('click', () => { index = i; setActive(index); reset(); });
    dotsWrap.appendChild(b);
  });
  setActive(index);

  const step = (dir=1) => { index = (index + dir + slides.length) % slides.length; setActive(index); };
  prev.addEventListener('click', () => { step(-1); reset(); });
  next.addEventListener('click', () => { step(1); reset(); });

  let timer = setInterval(step, 5000);
  const reset = () => { clearInterval(timer); timer = setInterval(step, 5000); };
})();
