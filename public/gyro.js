/* Sinan Robo hero：光线步进渲染的精密陀螺仪 —— 三层金属环 + 琥珀色核心。无依赖，拖动可转，鼠标视差。 */
(function(){var cv=document.getElementById("gyro3d");if(!cv)return;var gl=cv.getContext("webgl2",{alpha:true,antialias:false,premultipliedAlpha:true});if(!gl){cv.remove();return;}
var reduce=matchMedia("(prefers-reduced-motion: reduce)").matches;
var vs="#version 300 es\nin vec2 p;void main(){gl_Position=vec4(p,0.,1.);}";
var fs=["#version 300 es","precision highp float;out vec4 O;uniform vec2 R;uniform float T;uniform vec2 M;uniform float S;uniform float H;",
"mat2 rot(float a){float c=cos(a),s=sin(a);return mat2(c,-s,s,c);}",
"float sdTorus(vec3 p,vec2 t){vec2 q=vec2(length(p.xz)-t.x,p.y);return length(q)-t.y;}",
"float sdSphere(vec3 p,float r){return length(p)-r;}",
"float sdCyl(vec3 p,float h,float r){vec2 d=abs(vec2(length(p.xz),p.y))-vec2(r,h);return min(max(d.x,d.y),0.)+length(max(d,0.));}",
"vec3 r1(vec3 p){p.xz*=rot(T*.35+S);p.yz*=rot(.5);return p;}",
"vec3 r2(vec3 p){p.xy*=rot(-T*.27+S*.6);p.yz*=rot(1.1);return p;}",
"vec3 r3(vec3 p){p.yz*=rot(T*.19+S*.3);p.xy*=rot(-.6);return p;}",
"vec2 map(vec3 p){",
" float core=sdSphere(p,.42);",
" vec3 a=r1(p);float ringA=sdTorus(a,vec2(1.05,.055));float pinA=min(sdCyl(a-vec3(1.05,0.,0.),.09,.035),sdCyl(a+vec3(1.05,0.,0.),.09,.035));",
" vec3 b=r2(p);float ringB=sdTorus(b,vec2(.80,.045));",
" vec3 c=r3(p);float ringC=sdTorus(c,vec2(.60,.032));",
" float axis=sdCyl(r3(p).xzy*vec3(1.,1.,1.),.62,.02);",
" float d=core;float id=0.;",
" if(ringA<d){d=ringA;id=1.;}if(pinA<d){d=pinA;id=1.;}if(ringB<d){d=ringB;id=2.;}if(ringC<d){d=ringC;id=3.;}if(axis<d){d=axis;id=3.;}",
" return vec2(d,id);}",
"vec3 nrm(vec3 p){vec2 e=vec2(.0012,0.);return normalize(vec3(map(p+e.xyy).x-map(p-e.xyy).x,map(p+e.yxy).x-map(p-e.yxy).x,map(p+e.yyx).x-map(p-e.yyx).x));}",
"float ao(vec3 p,vec3 n){float o=0.,s=.04;for(int i=1;i<=5;i++){float h=s*float(i);o+=(h-map(p+n*h).x)/pow(2.,float(i));}return clamp(1.-2.2*o,0.,1.);}",
"float shadow(vec3 ro,vec3 rd){float res=1.,t=.04;for(int i=0;i<28;i++){float h=map(ro+rd*t).x;res=min(res,12.*h/t);t+=clamp(h,.02,.2);if(res<.01||t>4.)break;}return clamp(res,0.,1.);}",
"vec3 env(vec3 d){float u=smoothstep(-.4,.9,d.y);vec3 sky=mix(vec3(.10,.09,.20),vec3(.62,.60,.85),u);float band=smoothstep(.15,.0,abs(d.y-.25))*.9;return sky+vec3(1.,.95,.9)*band*.6+vec3(1.,.6,.2)*smoothstep(.6,-.2,d.y)*.25;}",
"void main(){vec2 uv=(gl_FragCoord.xy-.5*R)/R.y;",
" float yaw=(M.x-.5)*.5,pit=(M.y-.5)*.35;vec3 ro=vec3(0.,.35,3.6);ro.yz*=rot(-pit-.15);ro.xz*=rot(yaw);",
" vec3 f=normalize(-ro),rgt=normalize(cross(f,vec3(0.,1.,0.))),up=cross(rgt,f);vec3 rd=normalize(f*2.0+uv.x*rgt+uv.y*up);",
" float t=0.;vec2 h;bool hit=false;for(int i=0;i<96;i++){h=map(ro+rd*t);if(h.x<.0008){hit=true;break;}t+=h.x*.9;if(t>9.)break;}",
" if(!hit){float g=exp(-pow(length(uv-vec2(0.,-.02))*2.6,2.))*.35;O=vec4(vec3(1.,.62,.22)*g*(.6+.4*H),g*.8);return;}",
" vec3 p=ro+rd*t,n=nrm(p);vec3 L=normalize(vec3(-.6,.9,.6)),L2=normalize(vec3(.7,.2,-.4));vec3 hv=normalize(L-rd);",
" float dif=clamp(dot(n,L),0.,1.),wrap=clamp(dot(n,L)*.5+.5,0.,1.),sh=shadow(p+n*.015,L),occ=ao(p,n);vec3 refl=env(reflect(rd,n));float fres=pow(1.-clamp(dot(n,-rd),0.,1.),4.);",
" vec3 col;",
" if(h.y<.5){",
"  vec3 q=p;q.xz*=rot(T*.15+S*.4);float lon=atan(q.z,q.x),lat=asin(clamp(q.y/.42,-1.,1.));",
"  float dl=.5-abs(fract(lon*3.82)-.5),db=.5-abs(fract(lat*3.0)-.5);float grid=clamp(smoothstep(.035,.0,dl)+smoothstep(.035,.0,db),0.,1.);",
"  float pulse=.85+.15*sin(T*2.+lat*6.);vec3 glow=vec3(1.,.58,.16)*pulse*(1.2+H*.6);vec3 shell=vec3(.06,.05,.08);",
"  col=mix(glow*(.35+.65*wrap),shell,grid*.9)+vec3(1.)*pow(clamp(dot(n,hv),0.,1.),80.)*.6+glow*fres*.5;",
" }else{",
"  vec3 base=h.y<1.5?vec3(.86,.87,.92):h.y<2.5?vec3(.95,.72,.35):vec3(.55,.56,.64);float metal=h.y<2.5?.9:.7;float rough=h.y<1.5?.25:.35;",
"  vec3 spec=refl*metal*(.55+.45*fres)+vec3(1.)*pow(clamp(dot(n,hv),0.,1.),mix(120.,30.,rough))*(.9*sh);",
"  vec3 diff=base*(.12+.55*wrap*mix(.45,1.,sh)+.2*clamp(dot(n,L2),0.,1.));",
"  col=(diff*(1.-metal*.6)+spec*base)*occ;",
"  col+=vec3(1.,.55,.15)*exp(-length(p)*1.6)*.35;   /* 核心的琥珀光照到环上 */",
" }",
" col=1.-exp(-col*1.25);col=pow(col,vec3(.4545));O=vec4(col,1.);}"].join("\n");
function sh(t,s){var o=gl.createShader(t);gl.shaderSource(o,s);gl.compileShader(o);if(!gl.getShaderParameter(o,gl.COMPILE_STATUS)){console.warn(gl.getShaderInfoLog(o));}return o;}
var pr=gl.createProgram();gl.attachShader(pr,sh(gl.VERTEX_SHADER,vs));gl.attachShader(pr,sh(gl.FRAGMENT_SHADER,fs));gl.linkProgram(pr);if(!gl.getProgramParameter(pr,gl.LINK_STATUS)){console.warn(gl.getProgramInfoLog(pr));return;}gl.useProgram(pr);
var buf=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buf);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,1,1]),gl.STATIC_DRAW);var pl=gl.getAttribLocation(pr,"p");gl.enableVertexAttribArray(pl);gl.vertexAttribPointer(pl,2,gl.FLOAT,false,0,0);
var U={};["R","T","M","S","H"].forEach(function(k){U[k]=gl.getUniformLocation(pr,k);});
var mx=.5,my=.5,tx=.5,ty=.5,spin=0,vel=0,drag=null,hov=0,th=0;
addEventListener("pointermove",function(e){tx=e.clientX/innerWidth;ty=1-e.clientY/innerHeight;if(drag){var dx=e.clientX-drag.x;drag.x=e.clientX;vel=dx*.004;spin+=vel;}});
cv.addEventListener("pointerenter",function(){th=1;});cv.addEventListener("pointerleave",function(){th=0;drag=null;});
cv.addEventListener("pointerdown",function(e){drag={x:e.clientX};cv.setPointerCapture(e.pointerId);});cv.addEventListener("pointerup",function(){drag=null;});
function size(){var b=cv.getBoundingClientRect();var s=Math.min(devicePixelRatio||1,1.5,900/Math.max(1,b.width));cv.width=Math.max(2,b.width*s|0);cv.height=Math.max(2,b.height*s|0);gl.viewport(0,0,cv.width,cv.height);}size();addEventListener("resize",size);
var t0=performance.now(),vis=true;new IntersectionObserver(function(es){vis=es[0].isIntersecting;}).observe(cv);
function frame(t){if(vis){mx+=(tx-mx)*.05;my+=(ty-my)*.05;hov+=(th-hov)*.06;if(!drag){spin+=vel;vel*=.94;}gl.uniform2f(U.R,cv.width,cv.height);gl.uniform1f(U.T,reduce?0:(t-t0)/1000);gl.uniform2f(U.M,mx,my);gl.uniform1f(U.S,spin);gl.uniform1f(U.H,hov);gl.drawArrays(gl.TRIANGLE_STRIP,0,4);}requestAnimationFrame(frame);}requestAnimationFrame(frame);})();
