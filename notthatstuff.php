<?php

	define('CK_REPLIQUE_ID', 'notthatstuff_replique_id');
	define('ICON_FILENAME', 'favicon.png');
	define('PERIOD_DURATION', 24 * 60 * 60);
	define('PORTRAIT_SIZE', 128);
	define('PORTRAITS_DIRNAME', 'portraits');
	define('PROGRESS_UPDATE_INTERVAL', 50);
	define('REPLIQUES_DIRNAME', '_repliques_');
	define('SPEAKER_FILENAME', 'speaker.txt');
	define('SPEECH_FILENAME', 'speech.flac');
	define('TEXT_FILENAME', 'text.txt');
	define('THIS_TITLE', 'not &ensp; that &ensp; stuff');

	$SPEAKER_NAMES = array(
		'Berezovetz' => 'м-р Бєрєзовєц',
		'Biun' => 'Бюн',
		'Zhdanov' => 'Жданов',
		'Latynina' => 'Латиніна',
		'Naki' => 'Накі',
		'Solovei' => 'Соловєй',
		'Tizengauzen' => 'Тізенґаузєн',
		'Tolstoevskii' => 'Толстоєвскій',
		'Shvetz' => 'Швєц',
		'Sheitelman' => 'Шейтєльман',
		'Yakovina' => 'Яковіна'
	);

	$num_repliques = count(array_diff(scandir(REPLIQUES_DIRNAME), array('.', '..')));

	$id = 1 + floor((time() % PERIOD_DURATION) * $num_repliques / PERIOD_DURATION);

	$show_allow_dialog = false;

	if (isset($_COOKIE[CK_REPLIQUE_ID])) {
		if (isset($_GET['back'])) {
			$id = 1 + ((((int)$_COOKIE[CK_REPLIQUE_ID]) + $num_repliques - 2) % $num_repliques);
		} else {
			$id = 1 + (((int)$_COOKIE[CK_REPLIQUE_ID]) % $num_repliques);
		}		
	} else {
		$show_allow_dialog = true;
	}
	setcookie(CK_REPLIQUE_ID, $id);

	$replique_dirpath = REPLIQUES_DIRNAME . '/' . $id;

	$speaker = file_get_contents($replique_dirpath . '/' . SPEAKER_FILENAME);
	$text_html = htmlspecialchars(file_get_contents($replique_dirpath . '/' . TEXT_FILENAME));

	$self_url = $_SERVER['PHP_SELF'];
	$self_dir_url = dirname($self_url);

	$icon_url = $self_dir_url . '/' . ICON_FILENAME;
	$speech_url = $self_dir_url . '/' . $replique_dirpath . '/' . SPEECH_FILENAME;
?>
<!DOCTYPE html>
<html>
	<head>
		<meta charset="UTF-8">
		<title><?=THIS_TITLE?></title>
		<link rel="icon" type="image/png" href="<?=$icon_url?>">
		<style>
			dialog::backdrop {
				background-color: #000000c0;
			}
			td.descript {
				width: 45%;
				vertical-align: top;
				color: #ff00ff;
				font-family: sans-serif;
			}
			td.sep {
				width: 10%;
			}
			td.descriptlink {
				vertical-align: top;
				text-align: center;
				color: #ff00ff;
				font-family: sans-serif;
				font-size: 125%;
			}
			a {
				font-family: sans-serif;
			}
			a:link{color: #00c000;}
			a:visited;{color: #008000;}
			a:hover{color: #00e000;}
			a:active;{color: #00ff00;}
		</style>
	</head>
	<body style="background-color: #000000;">
		<dialog id="dlgAllowPlay" style="background: #00000000; border: 0px;">
			<button id="btnPlayAudio" style="border-radius: 8px; cursor: pointer; background-color: #000080;"><p>Клацніть &#x25b6;&#xfe0f; щоб почати</p><p style="font-size: 1000%;">&#x25b6;&#xfe0f;</p><p>Click &#x25b6;&#xfe0f; to start</p></button>
		</dialog>
		<marquee direction="up" scrollamount="1" scrolldelay="250" style="width: 100%; height: 100%; color: #000000; background-color: #ff0000; font-family: monospace; text-align: center;"><b>&#x26a0;&#xfe0f; НЕБЕЗПЕКА ГЛИБОКОЇ ПІДРОБКИ &#x1f925; DEEPFAKEHAZARD &#x26a0;&#xfe0f; НЕБЕЗПЕКА ГЛИБОКОЇ ПІДРОБКИ &#x1f925; DEEPFAKEHAZARD &#x26a0;&#xfe0f; НЕБЕЗПЕКА ГЛИБОКОЇ ПІДРОБКИ &#x1f925;</b></marquee>
		<div style="width: 100%; text-align: center; font-size: 200%; color: #ffffff; font-family: monospace;">not &ensp; that &ensp; stuff</div>
		<hr color="#ffffff">
		<table width="100%"><tr><td style="width: 50%; vertical-align: top;">
<?php
	foreach ($SPEAKER_NAMES as $spkr=>$spkr_name) {
		$suffix = ($spkr == $speaker) ? 'on' : 'off';
		$border_style = ($spkr == $speaker) ? ' border: 2px solid #0000C0; border-radius: 16px; box-shadow: 0px 0px 8px #0000C0;' : '';
		$portrait_url = $self_dir_url . '/' . PORTRAITS_DIRNAME . '/' . $spkr . '_' . $suffix . '.gif';
?>
			<div style="display: inline-block; padding: 8px 8px 0px 8px; <?=$border_style?>">
				<img src="<?=$portrait_url?>" width="<?=PORTRAIT_SIZE?>" height="<?=PORTRAIT_SIZE?>" style="border-radius: 16px;" />
				<p style="width: 100%; text-align: center; color: #c0c0c0; font-family: sans-serif; -webkit-box-reflect: below -0.25em -webkit-gradient(linear, left top, left bottom, from(transparent), color-stop(25%, transparent), to(rgba(255, 255, 255, 0.5)));">&laquo;<?=$spkr_name?>&raquo;</p>
			</div>
<?php
	}
?>
		</td><td style="vertical-align: top;">
			<a href="<?=$self_url?>?back" style="text-decoration: none; font-size: 300%;">&#x23ea;</a>
		</td><td style="width: 45%; vertical-align: top;">
			<p style="color: #0000ff; font-family: sans-serif; text-align: center; -webkit-box-reflect: below -0.25em -webkit-gradient(linear, left top, left bottom, from(transparent), color-stop(25%, transparent), to(rgba(0, 0, 255, 0.75)));">&laquo;<?=$SPEAKER_NAMES[$speaker]?>&raquo;</p>
			<p style="color: #ffff00; text-align: justify;"><?=$text_html?></p>
			<audio id="audSpeech" autoplay><source src="<?=$speech_url?>" type="audio/flac"></audio>
			<progress id="prgPlay" max="1" value="0" style="width: 100%; accent-color: black; opacity: 50%;"></progress>
		</td><td style="vertical-align: top;">
			<a href="<?=$self_url?>" style="text-decoration: none; font-size: 300%;">&#x23e9;</a>
		</td></tr></table>
		<hr color="#ffffff">
		<div style="width: 100%; text-align: center; font-size: 150%; color: #404040; font-family: monospace;">in &ensp; a &ensp; mirror of LLM+TTS+VC</div>
		<marquee direction="down" scrollamount="1" scrolldelay="250" style="width: 100%; height: 100%; color: #000000; background-color: #ff0000; font-family: monospace; text-align: center;"><b>&#x26a0;&#xfe0f; НЕБЕЗПЕКА ГЛИБОКОЇ ПІДРОБКИ &#x1f925; DEEPFAKEHAZARD &#x26a0;&#xfe0f; НЕБЕЗПЕКА ГЛИБОКОЇ ПІДРОБКИ &#x1f925; DEEPFAKEHAZARD &#x26a0;&#xfe0f; НЕБЕЗПЕКА ГЛИБОКОЇ ПІДРОБКИ &#x1f925;</b></marquee>
		<table style="width: 100%;">
			<tr>
				<td class="descript">&#x1f352; Тож які трибки обертаються за лаштунками цієї шизофазійної вистави? <a href="https://uk.wikipedia.org/wiki/%D0%92%D0%B5%D0%BB%D0%B8%D0%BA%D0%B0_%D0%BC%D0%BE%D0%B2%D0%BD%D0%B0_%D0%BC%D0%BE%D0%B4%D0%B5%D0%BB%D1%8C">Великі мовні моделі</a>, навчені на автоматичних субтитрах з YouTube-каналів вищенаведених мовників, послідовно генерують репліки, кожну на основі двох попередніх, при цьому наступний мовник обирається цілком випадково. Інша <a href="https://uk.wikipedia.org/wiki/%D0%A8%D1%82%D1%83%D1%87%D0%BD%D0%B0_%D0%BD%D0%B5%D0%B9%D1%80%D0%BE%D0%BD%D0%BD%D0%B0_%D0%BC%D0%B5%D1%80%D0%B5%D0%B6%D0%B0">ШНМ</a>-модель, яка перетворює текст на мову із клонуванням голосу, навчена на монологах тих же персон, синтезує відповідні фрагменти мовлення. (Анімовані портрети зроблені просто з коротких YouTube-передпереглядів, без усякого ШІ (за винятком &laquo;гібрида&raquo; з XIX ст., для якого знадобилися <a href="https://aifaceswap.io/ai-face-morph/#face-swap-playground">обмінювач</a> та <a href="https://www.trynow.ai/animating-face">оживлювач</a>); лишаємо імітацію візуальної компоненти, скажімо синхронізацію губ, у якості вправи для читача.) Шоу складається з 1440 таких реплік, генерованих заздалегідь і закільцьованих із періодом у 24 години.</td>
				<td class="sep">&nbsp;</td>
				<td class="descript">&#x1f352; So, what gears are turning behind the curtains of this schizophasic performance? <a href="https://en.wikipedia.org/wiki/Large_language_model">Large language models</a>, trained on automatic subtitles from YouTube channels of aforementioned speakers, generate repliques sequentially, each based on two previous ones, at that the next speaker is chosen entirely randomly. Another <a href="https://en.wikipedia.org/wiki/Neural_network_(machine_learning)">ANN</a> model that transforms text to speech with voice cloning, trained on monologues of the same persons, synthesises corresponding fragments of speech. (Animated portraits were made simply from YouTube short previews, without any AI (except &ldquo;hybrid&rdquo; from XIX c., who required <a href="https://aifaceswap.io/ai-face-morph/#face-swap-playground">swapper</a> and <a href="https://www.trynow.ai/animating-face">animator</a>); we leave imitation of visual component, say lipsync, as an exercise to the reader.) The show consists of 1440 such repliques generated beforehand and looped with a period of 24 hours.</td>
			</tr>
			<tr><td class="descriptlink" colspan="3">&nbsp;</td></tr>
			<tr>
				<td class="descript">&#x1f352; З технічної точки зору тут немає нічогісінько принципово нового порівняно з</td>
				<td class="sep">&nbsp;</td>
				<td class="descript">&#x1f352; From technical point of view, there is nothing new in essence here, in comparison with</td>
			</tr>
			<tr><td class="descriptlink" colspan="3">&nbsp;</td></tr>
			<tr><td class="descriptlink" colspan="3"><a href="https://www.infiniteconversation.com/"><b>The Infinite Conversation</b> (2022)</a></td></tr>
			<tr><td class="descriptlink" colspan="3">&nbsp;</td></tr>
			<tr>
				<td class="descript">&mdash; напевне головного джерела &laquo;натхнення&raquo; даного проєкту, який навіть синтаксично не досягає рівня оригіналу, не кажучи вже про семантику. &laquo;Ідея&raquo; наповнення основної форми оцим змістом настільки ширяє у повітрі, як реакція на тих, хто знає відповідь на все-все-все, що й це (чергове?) її втілення не блищить новизною. А ще глибше в минулому</td>
				<td class="sep">&nbsp;</td>
				<td class="descript">&mdash; perhaps the main source of &ldquo;inspiration&rdquo; for this project, which even syntactically does not reach the level of the original, to say nothing of semantics. The &ldquo;idea&rdquo; to fill basic shape with this content so much soars in the air, kind of reaction to those who know the answer just for everything, that this (yet another?) realisation of it, too, does not glitter with novelty. And even deeper in the past,</td>
			</tr>
			<tr><td class="descriptlink" colspan="3">&nbsp;</td></tr>
			<tr><td class="descriptlink" colspan="3"><a href="https://www.jwz.org/dadadodo/dadadodo.cgi"><b>DadaDodo</b> (1998)</a></td></tr>
			<tr><td class="descriptlink" colspan="3">&nbsp;</td></tr>
			<tr><td class="descriptlink" colspan="3"><a href="https://en.wikipedia.org/wiki/Mark_V._Shaney"><b>Mark V. Shaney</b> (1984)</a></td></tr>
			<tr><td class="descriptlink" colspan="3">&nbsp;</td></tr>
			<tr>
				<td class="descript">&#x1f352; Аналітичне продовження? Глузування? Заздрість? Ненависть? Образа? Пародія? Паскудство? Провокація? Прояснення? Роздратування? Сповивання? Хайп? Нехай одна з цілей цього проєкту &mdash; пришвидшити створення писаних і неписаних законів, які він порушує. Допоки його &laquo;герої&raquo;, заходячи сюди, не відчувають нічого особливого, чогось не вистачає. Розуміння, що це можна була зробити набагато краще, дозоляє.</td>
				<td class="sep">&nbsp;</td>
				<td class="descript">&#x1f352; Analytic continuation? Mockery? Envy? Insult? Hate? Parody? Foulness? Provocation? Clarification? Irritation? Midwivery? Hype? Let one of the goals of this project be to speed up creation of the laws, written and unwritten, which it breaks. As long as its &ldquo;heroes&rdquo;, when they come here, do not feel anything special, something is missing. To understand that it could be done much better is vexing.</td>
			</tr>
			<tr><td class="descriptlink" colspan="3">&nbsp;</td></tr>
			<tr>
				<td class="descript">&#x1f352; От хіба з точки зору етики... усі проблеми, здійняті оригіналом, автоматично переносяться сюди, посилені болючістю &laquo;обговорюваних&raquo; тем. А фактично одної: <a href="https://uk.wikipedia.org/wiki/%D0%A0%D0%BE%D1%81%D1%96%D0%B9%D1%81%D1%8C%D0%BA%D0%B5_%D0%B2%D1%82%D0%BE%D1%80%D0%B3%D0%BD%D0%B5%D0%BD%D0%BD%D1%8F_%D0%B2_%D0%A3%D0%BA%D1%80%D0%B0%D1%97%D0%BD%D1%83_(%D0%B7_2022)">війни, яку почала і роками веде російська федерація, очолювана путіним-хуйлом, проти України</a> і яка (сюрприз) спровокована просто існуванням останньої (якщо маєте досвід дойобування до себе гопників, яким більше ні до кого дойобуватись, то знаєте 50% про цю війну і що вам потрібно робити з тою федерацією). Щоправда, ті ж проблеми послаблені безграмотністю (синтаксисом) й недоладністю (семантикою) генерованих текстів.</td>
				<td class="sep">&nbsp;</td>
				<td class="descript">&#x1f352; Well, maybe from ethics point of view... all issues raised by the original transfer here automatically, intensified by painfulness of themes being &ldquo;discussed&rdquo;. Actually, it is single theme: <a href="https://en.wikipedia.org/wiki/Russian_invasion_of_Ukraine">the war started and being carried on for years by russian federation, headed by putin-motherfucker, against Ukraine</a>, the war, which is (surprise) provoked simply by existence of the latter (if you have an experience of mobsters badgerfucking with you because they have no one else to badgerfuck with, then you know 50% about this war and what you must do with that federation). Although these very issues are diminished by illiteracy (syntax) and incoherence (semantics) of generated texts.</td>
			</tr>
			<tr><td class="descriptlink" colspan="3">&nbsp;</td></tr>
			<tr>
				<td class="descript">&#x1f352; Поки уся примхлива іронія надто квола, аби нейтралізувати хоча б одну ракету чи дрон (а подеколи навіть подовжує усе це лайно), &mdash; Козаку Мамаю потрібний ТИ &#x1faf5;, та/або <a href="https://savelife.in.ua">донатити</a>, <a href="https://send.monobank.ua/jar/LgunsWua8">донатити</a>, донатити, <a href="https://itarmy.com.ua">ддосити</a>, <a href="https://forms.gle/FjvU3BvScHpGTCSR6">передавати</a>, <a href="https://prometheus.org.ua/prometheus-free/osint-open-source-intelligence/">вчитися</a>, <a href="https://drukarnia.com.ua">вчитися</a>, вчитися, допомагати... не заважати (заважати тим, хто заважає) &mdash; як мінімум; це лише кілька ходів довгої гри, кінця якої не побачить жодна фігура.</td>
				<td class="sep">&nbsp;</td>
				<td class="descript">&#x1f352; While all the fancy irony is too feeble to neutralise a single rocket or drone (and sometimes even prolongs all this shit), &mdash; Cossack Mamai needs YOU &#x1faf5;, and/or <a href="https://savelife.in.ua">donate</a>, <a href="https://send.monobank.ua/jar/LgunsWua8">donate</a>, donate, <a href="https://itarmy.com.ua">ddos</a>, <a href="https://forms.gle/FjvU3BvScHpGTCSR6">transfer</a>, <a href="https://prometheus.org.ua/prometheus-free/osint-open-source-intelligence/">learn</a>, <a href="https://drukarnia.com.ua">learn</a>, learn, aid... do not impede (impede those who impede) &mdash; at least; these are only few moves of the long game, the end of which no piece will see.</td>
			</tr>
			<tr><td class="descriptlink" colspan="3">&nbsp;</td></tr>
			<tr>
				<td class="descript">&#x1f352; &laquo;Цільова аудиторія&raquo; даного проєкту має власне розщеплення: ті, кого цікавить технічний бік, не слухають цих &laquo;експертів&raquo;, а ті, хто прислухаються до них, байдужі до цих &laquo;дрібниць&raquo; ШІ... переважно.</td>
				<td class="sep">&nbsp;</td>
				<td class="descript">&#x1f352; &ldquo;Target auditory&rdquo; of this project has its own schism: ones who are interested in technical side don't listen to these &ldquo;experts&rdquo;, and ones who hark to them are indifferent to these AI &ldquo;minutiae&rdquo;... mostly.</td>
			</tr>
			<tr><td class="descriptlink" colspan="3">&nbsp;</td></tr>
			<tr>
				<td class="descript">&#x1f352; Деякі мовники були знайдені за наступними статтями:</td>
				<td class="sep">&nbsp;</td>
				<td class="descript">&#x1f352; Some of the speakers were found from the following articles:</td>
			</tr>
			<tr><td class="descriptlink" colspan="3">&nbsp;</td></tr>
			<tr><td class="descriptlink" colspan="3"><a href="https://www.pravda.com.ua/articles/2025/02/27/7500476">pravda.com.ua/articles/2025/02/27/7500476</a><br>&nbsp;<br><a href="https://texty.org.ua/articles/114535">texty.org.ua/articles/114535</a></td></tr>
			<tr><td class="descriptlink" colspan="3">&nbsp;</td></tr>
			<tr>
				<td class="descript">&#x1f352; Вихідний код із детальнішими поясненнями та інструкціями з використання, а також текстові та мовленнєві набори даних, застосовані для навчання:</td>
				<td class="sep">&nbsp;</td>
				<td class="descript">&#x1f352; The source with more detailed explanations and instructions on usage, also text and speech datasets used for training:</td>
			</tr>
			<tr><td class="descriptlink" colspan="3">&nbsp;</td></tr>
			<tr><td class="descriptlink" colspan="3"><a href="https://github.com/Sunkware/notthatstuff/">github.com/Sunkware/notthatstuff</a> or <a href="<?=$self_dir_url?>/notthatstuff-latest.tar.gz">notthatstuff-latest.tar.gz</a> (36 K)<br><a href="<?=$self_dir_url?>/nts_train_data_text.zpaq">nts_train_data_text.zpaq</a> (54 M)<br><a href="<?=$self_dir_url?>/nts_train_data_speech.tar">nts_train_data_speech.tar</a> (57 M)</td></tr>
			<tr><td class="descriptlink" colspan="3">&nbsp;</td></tr>
			<tr>
				<td class="descript">&#x1f352; Повторіть ці результати, аби впевнитися, що ніякі додаткові &laquo;переконання&raquo;, &mdash; окрім тих, що їх мовники розділяли з самого початку, &mdash; не були таємно внесені у моделі, порушуючи об'єктивність експерименту. Проте будьте готові, що від деяких виразів, котрі вигулькнуть у цьому вареві, ваш особистий зрадометр зашкалить.</td>
				<td class="sep">&nbsp;</td>
				<td class="descript">&#x1f352; Replicate these results to be certain that no additional &ldquo;beliefs&rdquo;, &mdash; except the ones the speakers were convinced of in the first place, &mdash; were smuggled into the models, violating the objectivity of the experiment. Expect some expressions leaping out from this brew to make your personal betrayal-meter go off scale though.</td>
			</tr>
			<tr><td class="descriptlink" colspan="3">&nbsp;</td></tr>
			<tr>
				<td class="descript">&#x1f352; Враховуючи легкість повторюваності, зокрема через майже однаковість параметрів навчання для усіх мовників, доступ до навчених моделей тут ні до чого; все рівно вони вельми низької якості.</td>
				<td class="sep">&nbsp;</td>
				<td class="descript">&#x1f352; Taking into account the easiness of replication, in particular due to training parameters being almost identical for all speakers, access to trained models is needless here; they are of quite low quality all the same.</td>
			</tr>
			<tr><td class="descriptlink" colspan="3">&nbsp;</td></tr>
			<tr>
				<td class="descript">&#x1f352; &mdash; Чому без прапора? &mdash; <span style="font-size: 200%; vertical-align: middle;">&#x1f1fa;&#x1f1e6;</span> &mdash; Чого такий малий? &mdash; <span style="font-size: 800%; vertical-align: middle;">&#x1f1fa;&#x1f1e6;</span> &mdash; Нащо таки-- &mdash; <a href="https://www.dourish.com/goodies/see-figure-1.html">Дивись малюнок 1</a>.</td>
				<td class="sep">&nbsp;</td>
				<td class="descript">&#x1f352; &mdash; Why without the flag? &mdash; <span style="font-size: 200%; vertical-align: middle;">&#x1f1fa;&#x1f1e6;</span> &mdash; Why so small? &mdash; <span style="font-size: 800%; vertical-align: middle;">&#x1f1fa;&#x1f1e6;</span> &mdash; Why s-- &mdash; <a href="https://www.dourish.com/goodies/see-figure-1.html">See figure 1</a>.</td>
			</tr>
		</table>
	</body>

	<script type="text/javascript">
		audSpeech.addEventListener("ended", function() {
			window.location.replace("<?=$self_url?>");
		}, false);

		window.setInterval(function() {
			prgPlay.value = audSpeech.currentTime / audSpeech.duration;
		}, <?=PROGRESS_UPDATE_INTERVAL?>);

<?php
	if ($show_allow_dialog) {
?>
		window.addEventListener("load", function() {
			dlgAllowPlay.showModal();
		}, false);

		btnPlayAudio.addEventListener("click", function() {
			dlgAllowPlay.close();
			audSpeech.play();
		})
<?php
	}
?>
	</script>
</html>
