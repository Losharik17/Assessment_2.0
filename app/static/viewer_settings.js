$("#start").inputmask({
    clearMaskOnLostFocus : false,
    mask: "D.M.Y",
    placeholder: "дд.мм.гг",
    definitions: {
        "Y": {
            validator: function (chrs, buffer, pos, strict, opts) {
                let valExp = new RegExp("[0-9][0-9]");
                return valExp.test(chrs);
            },
            cardinality: 2,
            prevalidator: [
                { validator: "[0-9]", cardinality: 1 },
                { validator: "[0-9][0-9]", cardinality: 2 },
            ]
        },
        "M": {
            validator: function (chrs, buffer, pos, strict, opts) {
                let valExp2 = new RegExp("0[1-9]|1[0-2]");
                return valExp2.test(chrs);
            },
            cardinality: 2,
            prevalidator: [
                { validator: "[01]", cardinality: 1 },
                { validator: "0[1-9]", cardinality: 2 },
                { validator: "1[1-2]", cardinality: 2 },
            ]
        },
        "D": {
            validator: function (chrs, buffer, pos, strict, opts) {
                let valExp3 = new RegExp("0[1-9]|[12][0-9]|3[01]");
                return valExp3.test(chrs);
            },
            cardinality: 2,
            prevalidator: [
                { validator: "[0-3]", cardinality: 1 },
                { validator: "0[1-9]", cardinality: 2 },
                { validator: "(1|2)[0-9]", cardinality: 2 },
                { validator: "3[0-1]", cardinality: 2 },
            ]
        },
    }
});

$("#end").inputmask({
    clearMaskOnLostFocus : false,
    mask: "D.M.Y",
    placeholder: "дд.мм.гг",
    definitions: {
        "Y": {
            validator: function (chrs, buffer, pos, strict, opts) {
                let valExp = new RegExp("[0-9][0-9]");
                return valExp.test(chrs);
            },
            cardinality: 2,
            prevalidator: [
                { validator: "[0-9]", cardinality: 1 },
                { validator: "[0-9][0-9]", cardinality: 2 },
            ]
        },
        "M": {
            validator: function (chrs, buffer, pos, strict, opts) {
                let valExp2 = new RegExp("0[1-9]|1[0-2]");
                return valExp2.test(chrs);
            },
            cardinality: 2,
            prevalidator: [
                { validator: "[01]", cardinality: 1 },
                { validator: "0[1-9]", cardinality: 2 },
                { validator: "1[1-2]", cardinality: 2 },
            ]
        },
        "D": {
            validator: function (chrs, buffer, pos, strict, opts) {
                let valExp3 = new RegExp("0[1-9]|[12][0-9]|3[01]");
                return valExp3.test(chrs);
            },
            cardinality: 2,
            prevalidator: [
                { validator: "[0-3]", cardinality: 1 },
                { validator: "0[1-9]", cardinality: 2 },
                { validator: "(1|2)[0-9]", cardinality: 2 },
                { validator: "3[0-1]", cardinality: 2 },
            ]
        },
    }
});