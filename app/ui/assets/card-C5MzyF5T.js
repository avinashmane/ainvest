import{Dt as e,S as t,i as n,lt as r,st as i,ut as a,wt as o,yt as s}from"./auth-COB8MGlN.js";var c=t.extend({name:`card`,style:`
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
`,classes:{root:`p-card p-component`,header:`p-card-header`,body:`p-card-body`,caption:`p-card-caption`,title:`p-card-title`,subtitle:`p-card-subtitle`,content:`p-card-content`,footer:`p-card-footer`}}),l={name:`Card`,extends:{name:`BaseCard`,extends:n,style:c,provide:function(){return{$pcCard:this,$parentInstance:this}}},inheritAttrs:!1};function u(t,n,c,l,u,d){return o(),a(`div`,s({class:t.cx(`root`)},t.ptmi(`root`)),[t.$slots.header?(o(),a(`div`,s({key:0,class:t.cx(`header`)},t.ptm(`header`)),[e(t.$slots,`header`)],16)):r(``,!0),i(`div`,s({class:t.cx(`body`)},t.ptm(`body`)),[t.$slots.title||t.$slots.subtitle?(o(),a(`div`,s({key:0,class:t.cx(`caption`)},t.ptm(`caption`)),[t.$slots.title?(o(),a(`div`,s({key:0,class:t.cx(`title`)},t.ptm(`title`)),[e(t.$slots,`title`)],16)):r(``,!0),t.$slots.subtitle?(o(),a(`div`,s({key:1,class:t.cx(`subtitle`)},t.ptm(`subtitle`)),[e(t.$slots,`subtitle`)],16)):r(``,!0)],16)):r(``,!0),i(`div`,s({class:t.cx(`content`)},t.ptm(`content`)),[e(t.$slots,`content`)],16),t.$slots.footer?(o(),a(`div`,s({key:1,class:t.cx(`footer`)},t.ptm(`footer`)),[e(t.$slots,`footer`)],16)):r(``,!0)],16)],16)}l.render=u;export{l as t};