/**
 * ABRIENDO EL TARRO - Generador de Google Form (Retrotarros)
 * ---------------------------------------------------------------
 * Crea automaticamente el formulario que se le manda a los coleccionistas:
 * trae "como va el capitulo" + todas las preguntas + subida de fotos/videos,
 * y enlaza una planilla de respuestas.
 *
 * COMO USAR (una sola vez, ~2 minutos):
 *   1. Entra a  https://script.google.com  con tu cuenta de Retrotarros.
 *   2. Click "Nuevo proyecto".
 *   3. Borra el codigo de ejemplo y pega TODO este archivo.
 *   4. Arriba, en la lista de funciones, deja seleccionada
 *      "crearFormAbriendoElTarro" y aprieta "Ejecutar".
 *   5. Te va a pedir permisos (es tu propia cuenta) -> Autorizar.
 *   6. Abre el menu "Ver > Registro" (o "Ejecuciones") y ahi salen 3 links:
 *        - Form para LLENAR  (este es el que mandas a los invitados)
 *        - Form para EDITAR  (por si quieres cambiar algo a mano)
 *        - Planilla de RESPUESTAS (aca llegan las postulaciones)
 *
 * NOTA sobre subir fotos/videos: Google Forms exige que el invitado tenga
 * sesion iniciada en Google para subir archivos. Por eso ademas dejamos un
 * campo de TEXTO para pegar un link (Drive / WeTransfer / Google Photos), asi
 * cualquiera puede mandar su material aunque no use Google.
 */

function crearFormAbriendoElTarro() {
  var form = FormApp.create('ABRIENDO EL TARRO - Postula tu coleccion (Retrotarros)');

  form.setDescription(
    'Gracias por querer abrir tu tarro!\n\n' +
    'Abriendo el Tarro es el segmento de Retrotarros donde invitamos a coleccionistas ' +
    'a mostrar lo suyo. Da lo mismo que coleccionas (consolas, cartuchos, figuras, ' +
    'revistas, perifericos, juguetes, lo que sea): lo que nos importa es la NOSTALGIA, ' +
    'la historia detras de cada pieza.\n\n' +
    'Tu coleccion es la estrella. No hay respuestas malas, no es concurso, y no importa ' +
    'cuanto valen las cosas: importa lo que significan para ti.\n\n' +
    '--- COMO VA EL CAPITULO ---\n' +
    '1) Te presentamos: quien eres y como partiste.\n' +
    '2) Tu ficha de coleccionista.\n' +
    '3) Recorremos tu coleccion por categorias.\n' +
    '4) LAS JOYAS: las piezas que TU eliges como las mas especiales.\n' +
    '5) La joya de la corona: tu numero uno.\n' +
    '6) Cierre: que santo grial persigues y donde te pueden seguir.\n\n' +
    'Este formulario nos da todo lo que necesitamos para armar tu episodio. ' +
    'Mientras mas detalle, mejor queda, pero no te estreses: lo pulimos juntos.'
  );

  form.setCollectEmail(true);
  form.setProgressBar(true);
  form.setAllowResponseEdits(true);

  // ============================================================
  // SECCION 1 · TU FICHA
  // ============================================================
  form.addSectionHeaderItem()
    .setTitle('1) Tu ficha de coleccionista')
    .setHelpText('Lo basico para presentarte en el episodio.');

  form.addTextItem()
    .setTitle('Nombre (o como quieres que te presentemos)')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Coleccionas desde (ano o edad a la que partiste)');

  form.addTextItem()
    .setTitle('Que coleccionas (en una frase)')
    .setHelpText('Ej: "consolas y cartuchos de los 90", "figuras de juegos de pelea", "revistas retro".')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Cuantas piezas tienes (aprox)');

  form.addTextItem()
    .setTitle('De donde eres (ciudad, pais)');

  form.addParagraphTextItem()
    .setTitle('Lo mas preciado de tu coleccion (en una linea)');

  // ============================================================
  // SECCION 2 · TU ORIGEN (la nostalgia)
  // ============================================================
  form.addPageBreakItem()
    .setTitle('2) Tu origen')
    .setHelpText('Aca vive la nostalgia. Cuentanoslo con calma, no hay respuestas perfectas.');

  form.addParagraphTextItem()
    .setTitle('Cual fue la primera pieza de tu coleccion y como llego a ti?');

  form.addParagraphTextItem()
    .setTitle('Que te engancho a coleccionar? Hubo un momento exacto?');

  form.addMultipleChoiceItem()
    .setTitle('Coleccionas mas para...')
    .setChoiceValues(['Jugar / usar', 'Tener / completar', 'Recordar', 'Un poco de todo'])
    .showOtherOption(true);

  // ============================================================
  // SECCION 3 · TUS CATEGORIAS
  // ============================================================
  form.addPageBreakItem()
    .setTitle('3) Las categorias de tu coleccion')
    .setHelpText('Como tienes (o agruparias) tu coleccion. Recorremos cada una en el episodio.');

  form.addParagraphTextItem()
    .setTitle('Lista tus categorias y cuantas piezas aprox tiene cada una')
    .setHelpText('Ej:\nConsolas - 12\nCartuchos SNES - 40\nFiguras - 25\nRevistas - 15')
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle('Por cada categoria, 2 o 3 piezas destacadas que quieras que mostremos')
    .setHelpText('No tienen que ser las mas caras, las que tu quieras lucir.');

  // ============================================================
  // SECCION 4 · TUS JOYAS (las eliges tu)
  // ============================================================
  form.addPageBreakItem()
    .setTitle('4) Tus joyas')
    .setHelpText('Las piezas que exceden lo genial. Las que sacas del estante con orgullo. ' +
                 'Aca manda el corazon, no el precio. Llena las que quieras (3 a 5 ideales).');

  for (var i = 1; i <= 5; i++) {
    var requerida = (i <= 3); // las primeras 3 sugeridas; 4 y 5 opcionales
    form.addParagraphTextItem()
      .setTitle('JOYA ' + i + (requerida ? '' : ' (opcional)'))
      .setHelpText('Nombre de la pieza / ano / origen / la historia (como la conseguiste) / ' +
                   'por que es una joya para ti.');
  }

  // ============================================================
  // SECCION 5 · LA JOYA DE LA CORONA
  // ============================================================
  form.addPageBreakItem()
    .setTitle('5) Tu joya de la corona')
    .setHelpText('La numero uno. La que jamas venderias.');

  form.addTextItem()
    .setTitle('Cual es tu joya de la corona?')
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle('Por que esa por sobre todas las demas?')
    .setRequired(true);

  // ============================================================
  // SECCION 6 · MATERIAL VISUAL
  // ============================================================
  form.addPageBreakItem()
    .setTitle('6) Material visual')
    .setHelpText('Para que se vea bonito en pantalla. Fotos del celular con buena luz funcionan perfecto.');

  // Subida nativa (requiere sesion Google del invitado)
  try {
    form.addFileUploadItem()
      .setTitle('Sube fotos / videos de tus piezas (sobre todo de las joyas)')
      .setHelpText('Requiere tener sesion iniciada en Google. Si no puedes, usa el campo de link de abajo.');
  } catch (e) {
    // addFileUploadItem puede fallar si la cuenta no permite uploads; seguimos con el link.
    Logger.log('Aviso: no se pudo agregar el campo de subida de archivos: ' + e);
  }

  // Alternativa por link (para cualquiera, sin sesion Google)
  form.addParagraphTextItem()
    .setTitle('O pega un link con tus fotos/videos')
    .setHelpText('Carpeta de Google Drive, Google Photos, WeTransfer, etc. Asegurate de que el link sea publico o accesible.');

  // ============================================================
  // SECCION 7 · CIERRE Y CONTACTO
  // ============================================================
  form.addPageBreakItem()
    .setTitle('7) Cierre y contacto')
    .setHelpText('Lo ultimo para coordinar la grabacion.');

  form.addParagraphTextItem()
    .setTitle('Que santo grial todavia persigues? (lo que te falta)');

  form.addTextItem()
    .setTitle('Donde te pueden seguir (Instagram, YouTube, TikTok...)');

  form.addMultipleChoiceItem()
    .setTitle('Como prefieres grabar?')
    .setChoiceValues(['Presencial en el estudio', 'Por videollamada', 'Me da lo mismo'])
    .showOtherOption(true);

  form.addTextItem()
    .setTitle('Telefono o contacto para coordinar')
    .setRequired(true);

  // ============================================================
  // Planilla de respuestas enlazada
  // ============================================================
  var ss = SpreadsheetApp.create('ABRIENDO EL TARRO - Respuestas (postulaciones)');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  // Mensaje de confirmacion al invitado
  form.setConfirmationMessage(
    'Listo! Recibimos tu postulacion para Abriendo el Tarro. ' +
    'Te vamos a contactar para coordinar la grabacion. Gracias por compartir tu tarro con Retrotarros!'
  );

  Logger.log('====================================================');
  Logger.log('FORM PARA LLENAR (mandar a invitados): ' + form.getPublishedUrl());
  Logger.log('FORM PARA EDITAR a mano:               ' + form.getEditUrl());
  Logger.log('PLANILLA DE RESPUESTAS:                ' + ss.getUrl());
  Logger.log('====================================================');
}
