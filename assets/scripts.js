


setTimeout(function mainFunction(){

    try {

		// Ini

        let flujo = document.getElementById("flujo");
        let viscocidad = document.getElementById('viscocidad');
        let api = document.getElementById('api');
        let numBB = document.getElementById('numUnidades');
        let numBPCV = document.getElementById('numEqpVar');
        let numBPCF = document.getElementById('numEqpFijo');
        let numBPT = document.getElementById('numEqpPar');
        let pDes = document.getElementById('pDes');

        alert("Bienvenido");

        document.addEventListener("mousemove", function(){

            if (flujo.value<3000 || flujo.value>7500)
            {
                flujo.style.backgroundColor = 'rgba(255, 1, 1, 0.344)';
            }
            else
            {
                flujo.style.backgroundColor = 'transparent';
            }

            if (viscocidad.value<30 || viscocidad.value>200)
            {
                viscocidad.style.backgroundColor = 'rgba(255, 1, 1, 0.344)';
            }
            else
            {
                viscocidad.style.backgroundColor = 'transparent';
            }

            if (api.value<15 || api.value>40)
            {
                api.style.backgroundColor = 'rgba(255, 1, 1, 0.344)';
            }
            else
            {
                api.style.backgroundColor = 'transparent';
            }

            if (pDes.value>1640)
            {
                pDes.style.backgroundColor = 'rgba(255, 1, 1, 0.344)';
            }
            else
            {
                pDes.style.backgroundColor = 'transparent';
            }

        })

		// Fin
	}

	catch(err) {

	  console.log(err)

	}

  console.log('Listener Added!');

}, 5000);

