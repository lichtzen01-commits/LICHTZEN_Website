/* Paint the poster first; fetch video only when the hero is visible. */
(()=>{'use strict';
const reduced=matchMedia('(prefers-reduced-motion: reduce)'),saveData=navigator.connection?.saveData;
const start=async(video,manual=false)=>{
 if(!manual&&(reduced.matches||saveData||video.dataset.userPaused))return;
 if(!video.dataset.mediaLoaded){
  video.dataset.mediaLoaded='true';
  for(const source of video.querySelectorAll('source[data-src]')){
   const path=source.dataset.src;
   source.src=window.LTZ_PORTABLE_ASSET?await window.LTZ_PORTABLE_ASSET(path):path;
   delete source.dataset.src;
  }
  video.defaultPlaybackRate=1;video.playbackRate=1;video.load();
 }
 video.play().catch(()=>{});
};
const observe=()=>document.querySelectorAll('video.hero-video').forEach(video=>{
 if(video.dataset.performanceReady)return;video.dataset.performanceReady='true';
 document.querySelector('[data-video-toggle]')?.addEventListener('click',()=>{if(!video.dataset.mediaLoaded)start(video,true);},{capture:true});
 // Pause/play control (WCAG 2.2.2): a user pause wins over the auto-resume on scroll or tab focus.
 const btn=video.parentElement.querySelector('.hero-video-toggle');
 if(btn){const T=window.LTZ_T||(x=>x);const set=p=>{btn.setAttribute('aria-pressed',String(p));btn.setAttribute('aria-label',T(p?'배경 영상 재생':'배경 영상 일시정지'));btn.classList.toggle('is-paused',p);};
  btn.addEventListener('click',()=>{if(video.paused||!video.dataset.mediaLoaded){delete video.dataset.userPaused;set(false);start(video,true);}else{video.dataset.userPaused='true';video.pause();set(true);}});
  set(!!(reduced.matches||saveData));}
 const activate=()=>{const idle=window.requestIdleCallback||((fn)=>setTimeout(fn,180));idle(()=>{if(document.visibilityState==='visible')start(video);},{timeout:1500});};
 if('IntersectionObserver'in window){const observer=new IntersectionObserver(entries=>{for(const entry of entries){video.dataset.inView=String(entry.isIntersecting);if(entry.isIntersecting){if(!video.dataset.mediaLoaded)activate();else if(video.dataset.viewportPaused){delete video.dataset.viewportPaused;start(video);}}else if(!video.paused){video.dataset.viewportPaused='true';video.pause();}}},{threshold:.05});observer.observe(video);}else activate();
 document.addEventListener('visibilitychange',()=>{if(document.hidden&&!video.paused){video.dataset.documentPaused='true';video.pause();}else if(!document.hidden&&video.dataset.documentPaused&&video.dataset.inView==='true'){delete video.dataset.documentPaused;start(video);}});
});
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>requestAnimationFrame(()=>requestAnimationFrame(observe)),{once:true});else requestAnimationFrame(()=>requestAnimationFrame(observe));
})();
