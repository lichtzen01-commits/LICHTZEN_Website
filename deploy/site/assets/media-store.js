(()=>{'use strict';
if(window.LTZMedia&&!document.documentElement.dataset.adminPreview&&document.documentElement.dataset.preview==='true'){
Promise.all([window.LTZMedia.get('poster'),window.LTZMedia.get('video')]).then(([poster,video])=>{
 const hero=document.querySelector('.hero');if(!hero)return;if(poster){const img=hero.querySelector('[data-hero-poster]');if(img)img.src=URL.createObjectURL(poster.blob);}
 let player=hero.querySelector('.hero-video'),controls=hero.querySelector('[data-video-toggle]');
 if(video?.disabled){player?.remove();controls?.remove();return;}
 if(video?.blob){if(!player){player=document.createElement('video');player.className='hero-video';player.muted=true;player.loop=true;player.playsInline=true;player.preload='metadata';hero.prepend(player);}player.src=URL.createObjectURL(video.blob);player.setAttribute('aria-label','리트젠 메인 가동 영상');
 if(!controls){controls=document.createElement('button');controls.className='video-toggle';controls.type='button';hero.querySelector('.hero-meta').append(controls);controls.addEventListener('click',()=>player.paused?player.play().catch(()=>{}):player.pause());player.addEventListener('play',()=>controls.textContent='영상 일시정지');player.addEventListener('pause',()=>controls.textContent='영상 재생');}
 controls.textContent='영상 재생';if(!matchMedia('(prefers-reduced-motion: reduce)').matches)player.play().catch(()=>{});}
}).catch(()=>{});
}

})();