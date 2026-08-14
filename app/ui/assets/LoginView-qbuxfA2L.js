import{$ as e,At as t,Dt as n,H as r,Ht as i,Kt as a,Lt as o,Nt as s,Ot as c,Pt as l,S as u,Ut as d,ct as f,ft as p,i as m,kt as h,lt as g,mt as _,n as v,pt as y,st as b,t as x,ut as S,wt as C,y as w,yt as T}from"./auth-COB8MGlN.js";import{t as E}from"./index-De9FbvO5.js";import{t as D}from"./card-C5MzyF5T.js";import{t as O}from"./button-CQcE7Yu6.js";var k=u.extend({name:`message`,style:`
    .p-message {
        display: grid;
        grid-template-rows: 1fr;
        border-radius: dt('message.border.radius');
        outline-width: dt('message.border.width');
        outline-style: solid;
    }

    .p-message-content-wrapper {
        min-height: 0;
    }

    .p-message-content {
        display: flex;
        align-items: center;
        padding: dt('message.content.padding');
        gap: dt('message.content.gap');
    }

    .p-message-icon {
        flex-shrink: 0;
    }

    .p-message-close-button {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        margin-inline-start: auto;
        overflow: hidden;
        position: relative;
        width: dt('message.close.button.width');
        height: dt('message.close.button.height');
        border-radius: dt('message.close.button.border.radius');
        background: transparent;
        transition:
            background dt('message.transition.duration'),
            color dt('message.transition.duration'),
            outline-color dt('message.transition.duration'),
            box-shadow dt('message.transition.duration'),
            opacity 0.3s;
        outline-color: transparent;
        color: inherit;
        padding: 0;
        border: none;
        cursor: pointer;
        user-select: none;
    }

    .p-message-close-icon {
        font-size: dt('message.close.icon.size');
        width: dt('message.close.icon.size');
        height: dt('message.close.icon.size');
    }

    .p-message-close-button:focus-visible {
        outline-width: dt('message.close.button.focus.ring.width');
        outline-style: dt('message.close.button.focus.ring.style');
        outline-offset: dt('message.close.button.focus.ring.offset');
    }

    .p-message-info {
        background: dt('message.info.background');
        outline-color: dt('message.info.border.color');
        color: dt('message.info.color');
        box-shadow: dt('message.info.shadow');
    }

    .p-message-info .p-message-close-button:focus-visible {
        outline-color: dt('message.info.close.button.focus.ring.color');
        box-shadow: dt('message.info.close.button.focus.ring.shadow');
    }

    .p-message-info .p-message-close-button:hover {
        background: dt('message.info.close.button.hover.background');
    }

    .p-message-info.p-message-outlined {
        color: dt('message.info.outlined.color');
        outline-color: dt('message.info.outlined.border.color');
    }

    .p-message-info.p-message-simple {
        color: dt('message.info.simple.color');
    }

    .p-message-success {
        background: dt('message.success.background');
        outline-color: dt('message.success.border.color');
        color: dt('message.success.color');
        box-shadow: dt('message.success.shadow');
    }

    .p-message-success .p-message-close-button:focus-visible {
        outline-color: dt('message.success.close.button.focus.ring.color');
        box-shadow: dt('message.success.close.button.focus.ring.shadow');
    }

    .p-message-success .p-message-close-button:hover {
        background: dt('message.success.close.button.hover.background');
    }

    .p-message-success.p-message-outlined {
        color: dt('message.success.outlined.color');
        outline-color: dt('message.success.outlined.border.color');
    }

    .p-message-success.p-message-simple {
        color: dt('message.success.simple.color');
    }

    .p-message-warn {
        background: dt('message.warn.background');
        outline-color: dt('message.warn.border.color');
        color: dt('message.warn.color');
        box-shadow: dt('message.warn.shadow');
    }

    .p-message-warn .p-message-close-button:focus-visible {
        outline-color: dt('message.warn.close.button.focus.ring.color');
        box-shadow: dt('message.warn.close.button.focus.ring.shadow');
    }

    .p-message-warn .p-message-close-button:hover {
        background: dt('message.warn.close.button.hover.background');
    }

    .p-message-warn.p-message-outlined {
        color: dt('message.warn.outlined.color');
        outline-color: dt('message.warn.outlined.border.color');
    }

    .p-message-warn.p-message-simple {
        color: dt('message.warn.simple.color');
    }

    .p-message-error {
        background: dt('message.error.background');
        outline-color: dt('message.error.border.color');
        color: dt('message.error.color');
        box-shadow: dt('message.error.shadow');
    }

    .p-message-error .p-message-close-button:focus-visible {
        outline-color: dt('message.error.close.button.focus.ring.color');
        box-shadow: dt('message.error.close.button.focus.ring.shadow');
    }

    .p-message-error .p-message-close-button:hover {
        background: dt('message.error.close.button.hover.background');
    }

    .p-message-error.p-message-outlined {
        color: dt('message.error.outlined.color');
        outline-color: dt('message.error.outlined.border.color');
    }

    .p-message-error.p-message-simple {
        color: dt('message.error.simple.color');
    }

    .p-message-secondary {
        background: dt('message.secondary.background');
        outline-color: dt('message.secondary.border.color');
        color: dt('message.secondary.color');
        box-shadow: dt('message.secondary.shadow');
    }

    .p-message-secondary .p-message-close-button:focus-visible {
        outline-color: dt('message.secondary.close.button.focus.ring.color');
        box-shadow: dt('message.secondary.close.button.focus.ring.shadow');
    }

    .p-message-secondary .p-message-close-button:hover {
        background: dt('message.secondary.close.button.hover.background');
    }

    .p-message-secondary.p-message-outlined {
        color: dt('message.secondary.outlined.color');
        outline-color: dt('message.secondary.outlined.border.color');
    }

    .p-message-secondary.p-message-simple {
        color: dt('message.secondary.simple.color');
    }

    .p-message-contrast {
        background: dt('message.contrast.background');
        outline-color: dt('message.contrast.border.color');
        color: dt('message.contrast.color');
        box-shadow: dt('message.contrast.shadow');
    }

    .p-message-contrast .p-message-close-button:focus-visible {
        outline-color: dt('message.contrast.close.button.focus.ring.color');
        box-shadow: dt('message.contrast.close.button.focus.ring.shadow');
    }

    .p-message-contrast .p-message-close-button:hover {
        background: dt('message.contrast.close.button.hover.background');
    }

    .p-message-contrast.p-message-outlined {
        color: dt('message.contrast.outlined.color');
        outline-color: dt('message.contrast.outlined.border.color');
    }

    .p-message-contrast.p-message-simple {
        color: dt('message.contrast.simple.color');
    }

    .p-message-text {
        font-size: dt('message.text.font.size');
        font-weight: dt('message.text.font.weight');
    }

    .p-message-icon {
        font-size: dt('message.icon.size');
        width: dt('message.icon.size');
        height: dt('message.icon.size');
    }

    .p-message-sm .p-message-content {
        padding: dt('message.content.sm.padding');
    }

    .p-message-sm .p-message-text {
        font-size: dt('message.text.sm.font.size');
    }

    .p-message-sm .p-message-icon {
        font-size: dt('message.icon.sm.size');
        width: dt('message.icon.sm.size');
        height: dt('message.icon.sm.size');
    }

    .p-message-sm .p-message-close-icon {
        font-size: dt('message.close.icon.sm.size');
        width: dt('message.close.icon.sm.size');
        height: dt('message.close.icon.sm.size');
    }

    .p-message-lg .p-message-content {
        padding: dt('message.content.lg.padding');
    }

    .p-message-lg .p-message-text {
        font-size: dt('message.text.lg.font.size');
    }

    .p-message-lg .p-message-icon {
        font-size: dt('message.icon.lg.size');
        width: dt('message.icon.lg.size');
        height: dt('message.icon.lg.size');
    }

    .p-message-lg .p-message-close-icon {
        font-size: dt('message.close.icon.lg.size');
        width: dt('message.close.icon.lg.size');
        height: dt('message.close.icon.lg.size');
    }

    .p-message-outlined {
        background: transparent;
        outline-width: dt('message.outlined.border.width');
    }

    .p-message-simple {
        background: transparent;
        outline-color: transparent;
        box-shadow: none;
    }

    .p-message-simple .p-message-content {
        padding: dt('message.simple.content.padding');
    }

    .p-message-outlined .p-message-close-button:hover,
    .p-message-simple .p-message-close-button:hover {
        background: transparent;
    }

    .p-message-enter-active {
        animation: p-animate-message-enter 0.3s ease-out forwards;
        overflow: hidden;
    }

    .p-message-leave-active {
        animation: p-animate-message-leave 0.15s ease-in forwards;
        overflow: hidden;
    }

    @keyframes p-animate-message-enter {
        from {
            opacity: 0;
            grid-template-rows: 0fr;
        }
        to {
            opacity: 1;
            grid-template-rows: 1fr;
        }
    }

    @keyframes p-animate-message-leave {
        from {
            opacity: 1;
            grid-template-rows: 1fr;
        }
        to {
            opacity: 0;
            margin: 0;
            grid-template-rows: 0fr;
        }
    }
`,classes:{root:function(e){var t=e.props;return[`p-message p-component p-message-`+t.severity,{"p-message-outlined":t.variant===`outlined`,"p-message-simple":t.variant===`simple`,"p-message-sm":t.size===`small`,"p-message-lg":t.size===`large`}]},contentWrapper:`p-message-content-wrapper`,content:`p-message-content`,icon:`p-message-icon`,text:`p-message-text`,closeButton:`p-message-close-button`,closeIcon:`p-message-close-icon`}}),A={name:`BaseMessage`,extends:m,props:{severity:{type:String,default:`info`},closable:{type:Boolean,default:!1},life:{type:Number,default:null},icon:{type:String,default:void 0},closeIcon:{type:String,default:void 0},closeButtonProps:{type:null,default:null},size:{type:String,default:null},variant:{type:String,default:null}},style:k,provide:function(){return{$pcMessage:this,$parentInstance:this}}};function j(e){"@babel/helpers - typeof";return j=typeof Symbol==`function`&&typeof Symbol.iterator==`symbol`?function(e){return typeof e}:function(e){return e&&typeof Symbol==`function`&&e.constructor===Symbol&&e!==Symbol.prototype?`symbol`:typeof e},j(e)}function M(e,t,n){return(t=N(t))in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function N(e){var t=P(e,`string`);return j(t)==`symbol`?t:t+``}function P(e,t){if(j(e)!=`object`||!e)return e;var n=e[Symbol.toPrimitive];if(n!==void 0){var r=n.call(e,t);if(j(r)!=`object`)return r;throw TypeError(`@@toPrimitive must return a primitive value.`)}return(t===`string`?String:Number)(e)}var F={name:`Message`,extends:A,inheritAttrs:!1,emits:[`close`,`life-end`],timeout:null,data:function(){return{visible:!0}},mounted:function(){var e=this;this.life&&setTimeout(function(){e.visible=!1,e.$emit(`life-end`)},this.life)},methods:{close:function(e){this.visible=!1,this.$emit(`close`,e)}},computed:{closeAriaLabel:function(){return this.$primevue.config.locale.aria?this.$primevue.config.locale.aria.close:void 0},dataP:function(){return r(M(M({outlined:this.variant===`outlined`,simple:this.variant===`simple`},this.severity,this.severity),this.size,this.size))}},directives:{ripple:v},components:{TimesIcon:E}};function I(e){"@babel/helpers - typeof";return I=typeof Symbol==`function`&&typeof Symbol.iterator==`symbol`?function(e){return typeof e}:function(e){return e&&typeof Symbol==`function`&&e.constructor===Symbol&&e!==Symbol.prototype?`symbol`:typeof e},I(e)}function L(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter(function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable})),n.push.apply(n,r)}return n}function R(e){for(var t=1;t<arguments.length;t++){var n=arguments[t]==null?{}:arguments[t];t%2?L(Object(n),!0).forEach(function(t){z(e,t,n[t])}):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):L(Object(n)).forEach(function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))})}return e}function z(e,t,n){return(t=B(t))in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function B(e){var t=V(e,`string`);return I(t)==`symbol`?t:t+``}function V(e,t){if(I(e)!=`object`||!e)return e;var n=e[Symbol.toPrimitive];if(n!==void 0){var r=n.call(e,t);if(I(r)!=`object`)return r;throw TypeError(`@@toPrimitive must return a primitive value.`)}return(t===`string`?String:Number)(e)}var H=[`data-p`],U=[`data-p`],W=[`data-p`],G=[`aria-label`,`data-p`],K=[`data-p`];function q(r,i,a,o,u,p){var m=c(`TimesIcon`),_=h(`ripple`);return C(),f(e,T({name:`p-message`,appear:``},r.ptmi(`transition`)),{default:s(function(){return[u.visible?(C(),S(`div`,T({key:0,class:r.cx(`root`),role:`alert`,"aria-live":`assertive`,"aria-atomic":`true`,"data-p":p.dataP},r.ptm(`root`)),[b(`div`,T({class:r.cx(`contentWrapper`)},r.ptm(`contentWrapper`)),[r.$slots.container?n(r.$slots,`container`,{key:0,closeCallback:p.close}):(C(),S(`div`,T({key:1,class:r.cx(`content`),"data-p":p.dataP},r.ptm(`content`)),[n(r.$slots,`icon`,{class:d(r.cx(`icon`))},function(){return[(C(),f(t(r.icon?`span`:null),T({class:[r.cx(`icon`),r.icon],"data-p":p.dataP},r.ptm(`icon`)),null,16,[`class`,`data-p`]))]}),r.$slots.default?(C(),S(`div`,T({key:0,class:r.cx(`text`),"data-p":p.dataP},r.ptm(`text`)),[n(r.$slots,`default`)],16,W)):g(``,!0),r.closable?l((C(),S(`button`,T({key:1,class:r.cx(`closeButton`),"aria-label":p.closeAriaLabel,type:`button`,onClick:i[0]||=function(e){return p.close(e)},"data-p":p.dataP},R(R({},r.closeButtonProps),r.ptm(`closeButton`))),[n(r.$slots,`closeicon`,{},function(){return[r.closeIcon?(C(),S(`i`,T({key:0,class:[r.cx(`closeIcon`),r.closeIcon],"data-p":p.dataP},r.ptm(`closeIcon`)),null,16,K)):(C(),f(m,T({key:1,class:[r.cx(`closeIcon`),r.closeIcon],"data-p":p.dataP},r.ptm(`closeIcon`)),null,16,[`class`,`data-p`]))]})],16,G)),[[_]]):g(``,!0)],16,U))],16)],16,H)):g(``,!0)]}),_:3},16)}F.render=q;var J={class:`min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center px-4`},Y={key:0,class:`px-6 pb-8 flex flex-col gap-4`},X=_({__name:`LoginView`,setup(e){let t=x(),n=w(),r=o(!1);async function c(){r.value=!0;try{await t.loginWithGoogle(),n.push(`/home`)}finally{r.value=!1}}return(e,n)=>(C(),S(`div`,J,[y(i(D),{class:`w-full max-w-sm shadow-lg`},{header:s(()=>[...n[0]||=[b(`div`,{class:`flex flex-col items-center pt-8 pb-2 px-6 gap-2`},[b(`span`,{class:`text-5xl select-none`},`📈`),b(`h1`,{class:`text-2xl font-bold tracking-tight text-slate-900 mt-1`},`AInvest`),b(`p`,{class:`md:text-lg text-slate-500 text-center leading-relaxed`},[p(` AI-powered investment game.`),b(`br`),p(` You start with ₹1\xA0Crore — make it grow. `)])],-1)]]),content:s(()=>[i(t).isLoggedIn?g(``,!0):(C(),S(`div`,Y,[i(t).error?(C(),f(i(F),{key:0,severity:`error`,closable:!1,class:`text-sm`},{default:s(()=>[p(a(i(t).error),1)]),_:1})):g(``,!0),y(i(O),{loading:r.value,disabled:r.value,severity:`secondary`,outlined:``,class:`w-full justify-center font-medium`,onClick:c},{default:s(()=>[...n[1]||=[b(`svg`,{class:`w-5 h-5 shrink-0 mr-3`,viewBox:`0 0 24 24`,xmlns:`http://www.w3.org/2000/svg`},[b(`path`,{d:`M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z`,fill:`#4285F4`}),b(`path`,{d:`M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z`,fill:`#34A853`}),b(`path`,{d:`M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z`,fill:`#FBBC05`}),b(`path`,{d:`M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z`,fill:`#EA4335`})],-1),p(` Continue with Google `,-1)]]),_:1},8,[`loading`,`disabled`]),n[2]||=b(`p`,{class:`text-center text-xs text-slate-400 mt-1`},[p(` By signing in you accept the `),b(`a`,{href:`/terms`,class:`text-blue-600 underline`},`terms of use`),p(`. `)],-1)]))]),_:1})]))}});export{X as default};