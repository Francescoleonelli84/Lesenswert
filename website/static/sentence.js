 // Parole da scrivere e cancellare
 var words = ["Kunst", "Digitalisierung"];
 var subheading = document.getElementById("auto-writing");
 var currentIndex = 0;

 // Funzione per scrivere e cancellare le parole a intervalli regolari
 function writeAndEraseWords() {
   var word = words[currentIndex];
   var currentIndexWord = 0;
   var isWriting = true;
   var interval = 100; // Intervallo tra le lettere in millisecondi

   function addOrRemoveLetter() {
     if (isWriting) {
       if (currentIndexWord < word.length) {
         subheading.textContent += word.charAt(currentIndexWord);
         currentIndexWord++;
         setTimeout(addOrRemoveLetter, interval);
       } else {
         isWriting = false;
         setTimeout(addOrRemoveLetter, 1000); // Intervallo tra le parole in millisecondi
       }
     } else {
       if (currentIndexWord > 0) {
         subheading.textContent = subheading.textContent.slice(0, -1);
         currentIndexWord--;
         setTimeout(addOrRemoveLetter, interval);
       } else {
         isWriting = true;
         currentIndex = (currentIndex + 1) % words.length;
         setTimeout(writeAndEraseWords, 1000); // Intervallo tra le parole in millisecondi
       }
     }
   }

   addOrRemoveLetter();
 }

 // Avvia la scrittura e cancellazione delle parole quando il documento è pronto
 document.addEventListener("DOMContentLoaded", writeAndEraseWords);