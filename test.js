!function(d) {
    if (d.location.host !== "lng-tgk-aime-gw.am-all.net") {
      return;
    }
    
    const post = (path, params) => {
        const form = d.createElement("form");
        form.method = 'POST';
        form.action = path;
        
        for (const key in params) {
            if (params.hasOwnProperty(key)) {
                const hiddenField = d.createElement('input');
                hiddenField.type = 'hidden';
                hiddenField.name = key;
                hiddenField.value = params[key];
        
                form.appendChild(hiddenField);
            }
        }
        d.body.appendChild(form);
        form.submit();
    }
    
    let otp = parseInt(d.location.hash.substring(1, 7) || prompt("Please enter the passcode provided by the bot"));
    
    if (isNaN(otp)) {
        return alert("Invalid code, please try again.");
    }
    
    let clal = Object.fromEntries(d.cookie.split(";").map(c => c.split("=")))["clal"];

    if (!clal || clal.length !== 64) {
        return alert("Couldn't retrieve login data, please logout and login, then try again.");
    }
    
    post("https://chunithm.beerpsi.tech/login", { otp, clal });
}(document)