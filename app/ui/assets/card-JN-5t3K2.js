import{S as e,i as t,lt as n,st as r,ut as i,vt as a,wt as o,xt as s}from"./auth-Bd0Ay6MP.js";var c=e.extend({name:`card`,style:`
    .p-card {
        background: dt('card.background');
        color: dt('card.color');
        box-shadow: dt('card.shadow');
        border-radius: dt('card.border.radius');
        display: flex;
        flex-direction: column;
    }

    .p-card-caption {
        display: flex;
        flex-direction: column;
        gap: dt('card.caption.gap');
    }

    .p-card-body {
        padding: dt('card.body.padding');
        display: flex;
        flex-direction: column;
        gap: dt('card.body.gap');
    }

    .p-card-title {
        font-size: dt('card.title.font.size');
        font-weight: dt('card.title.font.weight');
    }

    .p-card-subtitle {
        color: dt('card.subtitle.color');
    }
`,classes:{root:`p-card p-component`,header:`p-card-header`,body:`p-card-body`,caption:`p-card-caption`,title:`p-card-title`,subtitle:`p-card-subtitle`,content:`p-card-content`,footer:`p-card-footer`}}),l={name:`Card`,extends:{name:`BaseCard`,extends:t,style:c,provide:function(){return{$pcCard:this,$parentInstance:this}}},inheritAttrs:!1};function u(e,t,c,l,u,d){return s(),i(`div`,a({class:e.cx(`root`)},e.ptmi(`root`)),[e.$slots.header?(s(),i(`div`,a({key:0,class:e.cx(`header`)},e.ptm(`header`)),[o(e.$slots,`header`)],16)):n(``,!0),r(`div`,a({class:e.cx(`body`)},e.ptm(`body`)),[e.$slots.title||e.$slots.subtitle?(s(),i(`div`,a({key:0,class:e.cx(`caption`)},e.ptm(`caption`)),[e.$slots.title?(s(),i(`div`,a({key:0,class:e.cx(`title`)},e.ptm(`title`)),[o(e.$slots,`title`)],16)):n(``,!0),e.$slots.subtitle?(s(),i(`div`,a({key:1,class:e.cx(`subtitle`)},e.ptm(`subtitle`)),[o(e.$slots,`subtitle`)],16)):n(``,!0)],16)):n(``,!0),r(`div`,a({class:e.cx(`content`)},e.ptm(`content`)),[o(e.$slots,`content`)],16),e.$slots.footer?(s(),i(`div`,a({key:1,class:e.cx(`footer`)},e.ptm(`footer`)),[o(e.$slots,`footer`)],16)):n(``,!0)],16)],16)}l.render=u;export{l as t};