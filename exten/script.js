
    fetch('https://ghostyfiles.manpreetsingh12.repl.co/api?user=')
    .then(data => data.json())
    .then(Data => {
        const link1 = Data['links'][0];
        const link2 = Data['links'][1];
        const link3 = Data['links'][2];
        const link4 = Data['links'][3];
        const link5 = Data['links'][4];
        document.getElementById("a").href = link1
        document.getElementById("b").href = link2
        document.getElementById("c").href = link3
        document.getElementById("d").href = link4
        document.getElementById("e").href = link5
    })    
   