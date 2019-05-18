var tour = new Tour({
    name: 'MyTour',
    backdrop: true,
    template: "<div class='popover tour' style='max-width:40vw;'>" +
        "<div class='arrow'></div>" +
        "<h3 class='popover-title bg-primary  text-white'></h3>" +
        "<div class='popover-content'></div>" +
        "<div class='popover-navigation'>" +
        "<button class='btn btn-default' data-role='prev'>« Retour</button>" +
        "<button class='btn btn-default' data-role='next'>Suivant »</button>" +
        "<button class='btn btn-default' data-role='end'>Fin</button>" +
        "</div>" +
        "</div>",

    steps: [
        {
            orphan: true,
            title: "Bonjour !",
            content: "Bienvenue sur <b>LARD</b> ! <br> Notre application vous permettra de faire de l'art algorithmique. <br> Découvrons ensemble son fonctionnement."
        },
        {
            element: "#left-panel",
            title: "Menu",
            content: "Le menu de gauche regroupe toutes les catégories importantes de l'application."
        }, {
            path: "/dashboard/",
            element: "#dashboard",
            title: "Dashboard",
            content: "Clique sur dashboard pour avoir un aperçu général."
        },
        {
            element: "#card_pipelines",
            title: "Cartes",
            content: "Chaque carte te donne des informations sur l'ensemble du site.<br> Ici il s'agit du nombre de pipeline créé.<br> Nous verrons par la suite le but d'un pipeline."
        },
        {
            element: "#card_top",
            placement: "bottom",
            title: "Top",
            content: "Tu trouveras ici les pipelines en tendances."
        },
        {
            path: "/pipelines/",
            element: "#pipelines",
            title: "Traitements",
            content: "Clique sur traitements pour voir ou créer des pipelines."
        },
        {
            orphan: true,
            title: "Mais ?",
            content: "<b>Mais c'est quoi excatement un pipeline ?</b><br><br> Un pipeline ou traitement est un ensemble " +
                "de blocks de traitement,<br> connectés par des liaisons, permettant d'excuter une suite de traitements<br> sur une entrée donnée."
        },
        {
            element: "#card_pipe_list",
            placement: "bottom",
            title: "Liste",
            content: "Les différentes pipelines sont regroupés ici.<br> Tu pourras voir toutes tes créations mais aussi celles<br> des autres utilisateurs (si elles sont en mode public)."
        },
        {
            element: "#button_import_pipe",
            placement: "left",
            title: "Import",
            content: "Ce bouton te permet d'importer un autre pipeline."
        },
        {
            element: "#button_create_pipe",
            placement: "left",
            title: "Création",
            content: "C'est par là que tout commence.<br> Ce bouton permet de créer un pipeline."
        },
        {
            orphan: true,
            title: "Pipeline",
            content: "Nous allons maintenant voir la page d'édition d'un pipeline.<br> Pour ce faire il suffit de cliquer sur le nom du pipeline dans la liste."
        },
        {
            path: "/pipelines/Demo",
            element: "#addButton",
            placement: "left",
            title: "Ajout",
            content: "Pour commencer un pipeline, il faut des blocks.<br> Pour cela, clique sur le bouton Add.",
            onHidden: function (tour) {
                jQuery('#collapseExample').collapse('toggle');
            }
        },
        {
            element: "#collapseExample",
            title: "Création",
            placement: "bottom",
            content: "Voici le menu de création d'un block de traitement."
        },
        {
            element: "#type",
            placement: "bottom",
            title: "Création",
            content: "Dans un premier temps, choisis ton type de block.",
            onHidden: function (tour) {
                document.getElementById('name').value = "Blur1";
            }
        },
        {
            element: "#name",
            title: "Création",
            placement: "bottom",
            content: "Puis ajoute lui un nom."
        },
        {
            element: "#onLaunch",
            title: "Création",
            placement: "bottom",
            content: "On launch permet de définir si le block est le premier<br> à s'éxecuter au démarrage ou non.<br>Si coché, le block devient le point d'entrée du programme."
        },
        {
            element: "#pipeline",
            title: "Création",
            placement: "bottom",
            content: "Ce bouton permet d'importer un pipeline dans le pipeline existant.<br> Les deux pipelines seront mergés."
        },
        {
            element: "#create",
            title: "Création",
            placement: "bottom",
            content: "Clique sur create pour créer le block.",
            onHidden: function (tour) {
                jQuery('#collapseExample').collapse('toggle');
            }
        },
        {
            element: "#runButton",
            title: "Run",
            placement: "bottom",
            content: "Une fois tes blocks ajoutés et reliés.<br> Clique sur Run pour lancer l'éxecution."
        },
        {
            orphan: true,
            title: "Génération",
            content: "Une fois que tu as cliqué sur Run, tu auras<br> toutes les informations pour voir son résultat."
        },
        {
            path: "/results/",
            element: "#results",
            title: "Résultats",
            content: "Clique sur résultats pour afficher la liste des résultats."
        },
        {
            element: "#card_result",
            placement: "top",
            title: "Résultats",
            content: "Tous les résultats sont regroupés dans ce tableau."
        },
        {
            path: "/blocks/",
            element: "#blocks",
            title: "Blocks",
            content: "Clique sur blocks pour voir, créer ou éditer des blocks."
        },
        {
            element: "#card_block_list",
            title: "Blocks",
            placement: "top",
            content: "Tous les blocks sont regroupés dans ce tableau."
        },
        {
            element: "#import_block",
            title: "Blocks",
            placement: "left",
            content: "Ce bouton permet d'importer facilement un block."
        },
        {
            element: "#create_block",
            title: "Blocks",
            placement: "left",
            content: "Et là de créer un block."
        },
        {
            path: "/blocks/Blur/edit",
            element: "#ace-container",
            title: "Blocks",
            content: "La page d'édition / création d'un block se compose de plusieurs parties.<br> Voici la partie code, où tu pourras ajouter ton traitement en Python."
        },
        {
            element: "#cart_description",
            placement: "left",
            title: "Blocks",
            content: "Ici la description du block."
        },
        {
            element: "#card_inputs",
            placement: "left",



            title: "Blocks",
            content: "Ici tu vas pouvoir régler les entrées de ton block."
        },
        {
            element: "#button-add-input",
            placement: "left",
            title: "Blocks",
            content: "Pour ajouter une nouvelle entrée, clique sur Add."
        },
        {
            element: "#input_name",
            placement: "left",
            title: "Blocks",
            content: "Ajoute un nom à ton entrée."
        },
        {
            element: "#input_type",
            placement: "left",
            title: "Blocks",
            content: "Puis donne lui un type."
        },
        {
            element: "#save_inputs",
            placement: "left",
            title: "Blocks",
            content: "Enfin, clique sur Save pour sauvgarder."
        },
        {
            orphan: true,
            title: "C'est fini !",
            content: "Et voilà !<br> Tu viens de voir les bases pour utiliser notre application.<br>Amuses-toi bien !"
        }

    ]
});


document.getElementById('startTour').onclick = function () {
    tour.init();
    tour.restart();
};

if (!tour.ended()) {
    tour.start();
}


