// Localized overlay for per-interview content (field, role, intro, highlights,
// quote). English is the source of truth in data/interviews.json and is NOT
// repeated here — a missing locale or a missing interview id simply falls back
// to the English value (see tc() in composables/useI18n.js). Transcripts, names
// and org names stay English on purpose.
//
// When a new episode is added to interviews.json, it shows in English until an
// entry is added here for each language. Keyed by interview id.

export const interviewContent = {
  fr: {
    'xavier-eldridge': {
      field: 'Fabrication et robotique',
      role: 'Technicien de makerspace',
      intro:
        "Le parcours de Xavier a commencé avec un club de robotique au collège et une équipe FIRST au lycée qui a atteint les championnats du monde. Après un diplôme en informatique et des années à encadrer des équipes de robotique, il dirige aujourd'hui le makerspace d'Awty, gardant prêts les imprimantes 3D, graveurs laser, CNC et découpe jet d'eau, et accompagnant les élèves de l'idée à la réalisation finale.",
      highlights: [
        'Une journée à la tête du makerspace',
        'De la robotique FIRST à une carrière',
        'Machines préférées : la découpe jet d’eau et la CNC',
        'Les compétences qui comptent : l’enseignement et la gestion de projet',
      ],
      quote:
        'Donnez aux élèves les outils et l’accès, puis regardez où leur créativité les mène.',
    },
    'elliot-stokes': {
      field: 'Génie chimique',
      role: 'Directeur de la sécurité des procédés',
      intro:
        "La chimie n'était même pas la matière préférée d'Elliot, mais il aimait résoudre des problèmes, et le génie chimique l'a conquis lorsqu'il a vu comment l'architecture moléculaire détermine si un matériau est respirant, imperméable ou pare-balles. Après des années en R&D et un MBA, il dirige aujourd'hui la sécurité des procédés chez Honeywell, modélisant les risques catastrophiques pour qu'ils ne se réalisent jamais.",
      highlights: [
        'Le jour où la sécurité des procédés a pris tout son sens',
        'Monte-Carlo : des molécules au risque',
        'Les idées reçues sur les ingénieurs chimistes',
        'La sécurité des procédés et l’énergie verte',
      ],
      quote: 'En ingénierie, c’est ce que nous faisons : nous résolvons des problèmes.',
    },
    'mutahar-mehkri': {
      field: 'Aérospatiale',
      role: 'Ingénieur en sécurité des systèmes',
      intro:
        'Le tableau de visualisation de Mutahar au collège indiquait « astronaute ». Il a débuté au Johnson Space Center comme ingénieur en sécurité des sorties extravéhiculaires (EVA), surveillant les astronautes lors de leurs sorties dans l’espace depuis la Mission Evaluation Room. Après avoir travaillé sur la combinaison lunaire de nouvelle génération d’Axiom Space, il contribue aujourd’hui à certifier le Lunar Terrain Vehicle, le rover lunaire habité du programme Artemis.',
      highlights: [
        'Garder les astronautes en vie lors des sorties spatiales',
        'Pourquoi une fuite d’eau dans la combinaison peut vous noyer',
        'Certifier le Lunar Terrain Vehicle',
        'Les petits dangers sont les plus dangereux',
      ],
      quote: 'Parfois, les dangers les plus petits sont les plus dangereux.',
    },
    'aziz-bamik': {
      field: 'Énergie et maritime',
      role: 'Chef de projet → CBO',
      intro:
        "Aziz a rejoint GTT, l'entreprise française à l'origine de la technologie de confinement présente dans chaque méthanier, pour tester des matériaux cryogéniques à −196 °C. En choisissant la gestion de projet plutôt que l'ingénierie pure, il est passé des chantiers navals de Corée et du Japon à la direction mondiale du développement commercial, puis à l'ouverture de la filiale Amériques de GTT. Il est aujourd'hui Chief Business Officer d'Ascenz Marorka, la branche numérique de GTT.",
      highlights: [
        'Tester des matériaux à −196 °C',
        'Pourquoi il a choisi la gestion de projet',
        'De 30 % à 100 % de part de marché',
        'Pourquoi faire carrière dans l’énergie',
      ],
      quote: 'Soyez curieux, voyez les choses dans leur ensemble et trouvez un mentor.',
    },
    'nandini-harinath': {
      field: 'Systèmes spatiaux',
      role: 'Responsable des opérations de mission',
      intro:
        'Nandini a grandi en identifiant les constellations avec son père. À l’ISRO, elle est devenue chef de projet pour la conception de mission et directrice adjointe des opérations de la Mars Orbiter Mission, composant avec un délai de signal de 22 minutes dans un sens vers Mars. Elle dirige aujourd’hui les opérations de mission pour des satellites, « des médecins au chevet de leurs patients ».',
      highlights: [
        'Ses rôles au sein de la Mars Orbiter Mission',
        'Une journée dans les opérations de mission',
        'Commander un vaisseau à 22 minutes-lumière',
        'Comment la mission est restée à faible coût',
      ],
      quote:
        'L’espace ne tolère aucune erreur. C’est pourquoi le travail d’équipe est primordial.',
    },
    'michael-adelemoni': {
      field: 'Logiciel',
      role: 'Ingénieur logiciel',
      intro:
        "Michael a grandi à Ibadan, au Nigeria, a appris le JavaScript en imitant son grand frère, et a étudié l'informatique à Purdue, où des recherches au Data Mine l'ont mené à la modélisation météorologique par IA. Chez Google, il travaille sur l'infrastructure de test et consacre ses 20 % de temps libre à apprendre à l'IA à prédire les phénomènes météorologiques extrêmes.",
      highlights: [
        'La journée d’un ingénieur logiciel chez Google',
        'Comment l’IA transforme le métier',
        'La recherche, pas seulement les stages',
        'Des conseils pour les étudiants en informatique à l’ère de l’IA',
      ],
      quote: 'Soyez à l’aise avec l’IA, mais sachez travailler sans elle quand il le faut.',
    },
    'nancy-li': {
      field: 'Intégrité des pipelines',
      role: 'Ingénieure en services techniques d’intégrité',
      intro:
        "Nancy Li est ingénieure en services techniques d'intégrité chez Phillips 66. Elle a obtenu un master en génie mécanique, mais ne se destinait pas à l'ingénierie enfant. Elle travaille aujourd'hui sur l'intégrité et la maintenance des pipelines, veillant à ce que les projets soient sûrs et fiables. Son parcours montre que l'ingénierie peut commencer par un projet concret qui rend tangibles les connaissances apprises en cours.",
      highlights: [
        'Un chemin inattendu vers l’ingénierie',
        'Le projet concret qui a tout déclenché',
        'L’importance de la communication et du travail d’équipe',
        'Apprendre des défis et des échecs',
      ],
      quote: 'Je peux transposer mes connaissances dans le monde réel.',
    },
  },

  es: {
    'xavier-eldridge': {
      field: 'Fabricación y robótica',
      role: 'Técnico de makerspace',
      intro:
        'El camino de Xavier comenzó con un club de robótica en secundaria y un equipo FIRST en el instituto que llegó a los campeonatos mundiales. Tras una licenciatura en informática y años como mentor de equipos de robótica, ahora dirige el makerspace de Awty, manteniendo listas las impresoras 3D, grabadoras láser, CNC y cortadora por chorro de agua, y guiando a los estudiantes desde la idea hasta el proyecto terminado.',
      highlights: [
        'Un día dirigiendo el makerspace',
        'De la robótica FIRST a una carrera',
        'Máquinas favoritas: chorro de agua y CNC',
        'Las habilidades que importan: enseñanza y gestión de proyectos',
      ],
      quote:
        'Dales a los estudiantes las herramientas y el acceso, y luego observa a dónde los lleva su creatividad.',
    },
    'elliot-stokes': {
      field: 'Ingeniería química',
      role: 'Director de seguridad de procesos',
      intro:
        'La química ni siquiera era la asignatura favorita de Elliot, pero le gustaba resolver problemas, y la ingeniería química lo conquistó cuando vio cómo la arquitectura molecular decide si un material es transpirable, impermeable o a prueba de balas. Tras años en I+D y un MBA, ahora lidera la seguridad de procesos en Honeywell, modelando el riesgo catastrófico para que nunca se haga realidad.',
      highlights: [
        'El día en que la seguridad de procesos se volvió personal',
        'Monte Carlo: de las moléculas al riesgo',
        'Ideas erróneas sobre los ingenieros químicos',
        'La seguridad de procesos y la energía verde',
      ],
      quote: 'En la ingeniería, eso es lo que hacemos: resolvemos problemas.',
    },
    'mutahar-mehkri': {
      field: 'Aeroespacial',
      role: 'Ingeniero de seguridad de sistemas',
      intro:
        'El tablero de visión de Mutahar en secundaria decía «astronauta». Comenzó en el Johnson Space Center como ingeniero de seguridad de EVA, supervisando a los astronautas durante las caminatas espaciales desde la Mission Evaluation Room. Tras trabajar en el traje espacial lunar de nueva generación de Axiom Space, ahora ayuda a certificar el Lunar Terrain Vehicle, el vehículo lunar tripulado del programa Artemis.',
      highlights: [
        'Mantener con vida a los astronautas en las caminatas espaciales',
        'Por qué una fuga de agua en el traje puede ahogarte',
        'Certificar el Lunar Terrain Vehicle',
        'Los pequeños peligros son los peligrosos',
      ],
      quote: 'A veces los peligros más pequeños son los más peligrosos.',
    },
    'aziz-bamik': {
      field: 'Energía y sector marítimo',
      role: 'Gerente de proyectos → CBO',
      intro:
        'Aziz se incorporó a GTT, la empresa francesa detrás de la tecnología de contención que hay en cada buque metanero, para probar materiales criogénicos a −196 °C. Elegir la gestión de proyectos en lugar de la ingeniería pura lo llevó de los astilleros de Corea y Japón a la dirección global de desarrollo de negocio y a abrir la filial de GTT para las Américas. Hoy es Chief Business Officer de Ascenz Marorka, la rama digital de GTT.',
      highlights: [
        'Probar materiales a −196 °C',
        'Por qué eligió la gestión de proyectos',
        'Del 30 % al 100 % de cuota de mercado',
        'Por qué apostar por una carrera en la energía',
      ],
      quote: 'Sé curioso, mira el panorama general y encuentra un mentor.',
    },
    'nandini-harinath': {
      field: 'Sistemas espaciales',
      role: 'Líder de operaciones de misión',
      intro:
        'Nandini creció identificando constelaciones con su padre. En la ISRO llegó a ser jefa de proyecto de diseño de misión y directora adjunta de operaciones de la Mars Orbiter Mission, lidiando con un retardo de señal de 22 minutos de ida hacia Marte. Ahora lidera las operaciones de misión de satélites, «médicos que atienden a sus pacientes».',
      highlights: [
        'Sus funciones en la Mars Orbiter Mission',
        'Un día en las operaciones de misión',
        'Comandar una nave a 22 minutos luz de distancia',
        'Cómo la misión se mantuvo de bajo costo',
      ],
      quote: 'El espacio no tolera ningún error. Por eso el trabajo en equipo lo es todo.',
    },
    'michael-adelemoni': {
      field: 'Software',
      role: 'Ingeniero de software',
      intro:
        'Michael creció en Ibadán, Nigeria, aprendió JavaScript imitando a su hermano mayor y estudió informática en Purdue, donde la investigación en el Data Mine lo llevó al modelado meteorológico con IA. En Google trabaja en infraestructura de pruebas y dedica su 20 % de tiempo a enseñar a la IA a predecir fenómenos meteorológicos extremos.',
      highlights: [
        'El día de un ingeniero de software en Google',
        'Cómo la IA está cambiando el trabajo',
        'Investigación, no solo prácticas',
        'Consejos para estudiantes de informática en la era de la IA',
      ],
      quote:
        'Siéntete cómodo usando la IA, pero sé capaz de trabajar sin ella cuando lo necesites.',
    },
    'nancy-li': {
      field: 'Integridad de tuberías',
      role: 'Ingeniera de servicios técnicos de integridad',
      intro:
        'Nancy Li es ingeniera de servicios técnicos de integridad en Phillips 66. Obtuvo un máster en ingeniería mecánica, pero de pequeña no pensaba dedicarse a la ingeniería. Ahora trabaja en la integridad y el mantenimiento de tuberías, garantizando que los proyectos sean seguros y fiables. Su trayectoria demuestra que la ingeniería puede empezar con un proyecto práctico que hace que el conocimiento del aula se sienta real.',
      highlights: [
        'Un camino inesperado hacia la ingeniería',
        'El proyecto práctico que encajó',
        'La importancia de la comunicación y el trabajo en equipo',
        'Aprender de los retos y los fracasos',
      ],
      quote: 'Puedo llevar mis conocimientos al mundo real.',
    },
  },

  zh: {
    'xavier-eldridge': {
      field: '制作与机器人',
      role: '创客空间技术员',
      intro:
        'Xavier 的旅程始于初中的机器人社团和高中一支闯入世界锦标赛的 FIRST 战队。在取得计算机科学学位并多年指导机器人战队之后，他如今负责运营 Awty 的创客空间，让 3D 打印机、激光雕刻机、CNC 和水刀随时待命，并陪伴学生把想法变成成品。',
      highlights: [
        '运营创客空间的一天',
        '从 FIRST 机器人竞赛到职业生涯',
        '最爱的机器：水刀和 CNC',
        '真正重要的技能：教学与项目管理',
      ],
      quote: '给学生工具和使用的机会，然后看看他们的创造力会走向何方。',
    },
    'elliot-stokes': {
      field: '化学工程',
      role: '工艺安全总监',
      intro:
        '化学甚至都不是 Elliot 最喜欢的科目，但他擅长解决问题；当他看到分子结构如何决定一种材料是透气、防水还是防弹时，化学工程赢得了他的心。在多年的研发工作和取得 MBA 之后，他如今在 Honeywell 领导工艺安全，对灾难性风险进行建模，让它永远不会成为现实。',
      highlights: [
        '工艺安全真正触动他的那一天',
        '蒙特卡洛：从分子到风险',
        '关于化学工程师的误解',
        '工艺安全与绿色能源',
      ],
      quote: '在工程领域，这就是我们所做的：解决问题。',
    },
    'mutahar-mehkri': {
      field: '航空航天',
      role: '系统安全工程师',
      intro:
        'Mutahar 初中的愿景板上写着「宇航员」。他在 Johnson Space Center 起步，担任舱外活动（EVA）安全工程师，在任务评估室里监控太空行走中的宇航员。在参与 Axiom Space 新一代月面宇航服的工作之后，他如今协助认证 Lunar Terrain Vehicle——Artemis 计划的载人月球车。',
      highlights: [
        '在太空行走中保障宇航员的生命安全',
        '为何宇航服漏水会让你溺水',
        '认证 Lunar Terrain Vehicle',
        '微小的隐患才是危险的隐患',
      ],
      quote: '有时候，最微小的隐患才是最危险的。',
    },
    'aziz-bamik': {
      field: '能源与海事',
      role: '项目经理 → 首席商务官',
      intro:
        'Aziz 加入了 GTT——这家法国公司研发了每一艘 LNG 运输船内部的液货围护技术，他在 −196 °C 下测试低温材料。选择项目管理而非纯工程，让他从韩国和日本的造船厂，走到全球业务拓展负责人，再到开设 GTT 的美洲子公司。如今他是 GTT 数字化部门 Ascenz Marorka 的首席商务官。',
      highlights: [
        '在 −196 °C 下测试材料',
        '他为何选择项目管理',
        '从 30% 到 100% 的市场份额',
        '为何选择能源行业的职业道路',
      ],
      quote: '保持好奇，着眼全局，并找到一位导师。',
    },
    'nandini-harinath': {
      field: '空间系统',
      role: '任务运营负责人',
      intro:
        'Nandini 从小和父亲一起辨认星座。在 ISRO，她成为任务设计项目经理，以及火星轨道飞行器任务（Mars Orbiter Mission）的副运营总监，需要应对单程 22 分钟的对火星信号延迟。如今她负责卫星的任务运营——如同「照护病人的医生」。',
      highlights: [
        '她在火星轨道飞行器任务中的角色',
        '任务运营的一天',
        '指挥一艘 22 光分之外的航天器',
        '这项任务如何保持低成本',
      ],
      quote: '太空对错误零容忍。正因如此，团队合作就是一切。',
    },
    'michael-adelemoni': {
      field: '软件',
      role: '软件工程师',
      intro:
        'Michael 在尼日利亚的伊巴丹长大，通过模仿哥哥学会了 JavaScript，并在 Purdue 攻读计算机科学，在那里 Data Mine 的研究把他引向了 AI 气象建模。在 Google，他从事测试基础设施的工作，并用他 20% 的自由时间教 AI 预测极端天气。',
      highlights: [
        'Google 软件工程师的一天',
        'AI 正如何改变这份工作',
        '做研究，而不只是实习',
        '给 AI 时代计算机专业学生的建议',
      ],
      quote: '习惯于使用 AI，但在需要时也要能够脱离它工作。',
    },
    'nancy-li': {
      field: '管道完整性',
      role: '完整性技术服务工程师',
      intro:
        'Nancy Li 是 Phillips 66 的完整性技术服务工程师。她取得了机械工程硕士学位，但小时候并没有打算成为工程师。如今她从事管道完整性与维护工作，确保项目安全可靠。她的经历表明，工程之路可以始于一个动手项目，让课堂知识变得真切。',
      highlights: [
        '通往工程的意外之路',
        '让她豁然开朗的动手项目',
        '沟通与团队合作的重要性',
        '从挑战与失败中学习',
      ],
      quote: '我能把我的知识带入现实世界。',
    },
  },
}
