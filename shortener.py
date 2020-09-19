'''
     Author: Red Russian Army
'''

import nltk
nltk.download('stopwords')
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from Levenshtein import distance
import re, html
from multiprocessing.dummy import Pool as ThreadPool
from threading import Lock
from functools import partial

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class ParagraphShortener(metaclass=Singleton):
    WORDS_TOBE_EXCLUDED = [
                    "kaç","kaçtır",
                    "kim","kimdir",
                    "ne","nedir",
                    "hangi","hangisidir",
                    "nasıl","nasıldır",
                    "neresi","neresidir",
                    "neden","nedendir",
                    "nereden","neredendir",
                    "nerden","nerdendir"
                    ]
    SIMILAR_WORDS_RATIO = 0.12

    def __init__(self):
        self.dict_lock = Lock()
        self.filtered_text_lst = []
    def _get_filtered_text_lst(self):
        return self.filtered_text_lst
    def _append_filtered_text_lst(self, string):
        with self.dict_lock:
            self.filtered_text_lst.append(string)
    def _clear_filtered_text_lst(self):
        self.filtered_text_lst = []
    def _split_into_sentences(self, text):
        sent_tokens = sent_tokenize(text, language="turkish")
        sent_tokens = [re.sub("\n|\xa0", "", w) for w in sent_tokens]
        sent_tokens = [w.lower() for w in sent_tokens]
        return sent_tokens
    def _split_into_words(self, keyword):
        tokens = word_tokenize(keyword)
        tokens = [w.lower() for w in tokens]
        stop_words = set(stopwords.words('turkish'))
        words = [w for w in tokens if not w in stop_words]
        for word in words:
            for i in range(len(self.WORDS_TOBE_EXCLUDED)):
                if word == self.WORDS_TOBE_EXCLUDED[i]:
                    words.remove(word)
        return words
    def _filter_depending_on_distance(self, sentence, keyword_list):
        '''
            Excludes sentences taking into account Levenshtein distance method
        '''
        rmv_indexes = []
        rmv_buffer = []
        filtered_text = ""
        similar_words = 0
        words_list = sentence.split()
        for keyword in keyword_list:
            for w_index in range(len(words_list)):
                d = distance(keyword, words_list[w_index])
                lens = [len(keyword),len(words_list[w_index])]
                if d < min(max(lens[0],lens[1])*3/4,5):
                    similar_words += 1 
        word_amount = len(words_list)
        if word_amount > 0 and similar_words / word_amount > self.SIMILAR_WORDS_RATIO:
            self._append_filtered_text_lst(sentence)
    def _limit(self, text_lst, word_limit):
        text_list = text_lst
        rmv_indexes = []
        rmv_buffer = []
        i_base_txt = 0
        try:
            while i_base_txt < len(text_list):
                i_txt = i_base_txt + 1
                while len((text_list[i_base_txt]+" "+text_list[i_txt]).split()) < word_limit:
                    text_list[i_base_txt] += " " + text_list[i_txt]
                    rmv_indexes.append(i_txt)
                    i_txt += 1
                    if i_txt > len(text_list)-1:
                        break
                if len(rmv_indexes) > 0:
                    for i in rmv_indexes:
                        rmv_buffer.append(text_list[i]) 
                    for text in rmv_buffer:
                        text_list.remove(text)
                    rmv_indexes = []
                    rmv_buffer = []
                i_base_txt += 1
                if i_base_txt > len(text_list)-1:
                    break
        except Exception as e:
            print(f"Error while seperating into {word_limit} word-list. Exception: {e}")
        self.filtered_text_lst = text_list
    def _parallel_runner(self, text, keyword, threads=4):
        print("TOTAL INPUT WORD AMOUNT:", len(text.split()))
        
        sentence_list = self._split_into_sentences(text)
        keyword_list = self._split_into_words(keyword)
        filter_distance = partial(self._filter_depending_on_distance, keyword_list=keyword_list)
        pool = ThreadPool(threads)
        pool.map(filter_distance, sentence_list)
        pool.close()
        pool.join()
        self._limit(self.filtered_text_lst, 260)
        filtered_text = self._get_filtered_text_lst()
        self._clear_filtered_text_lst()

        w_cnt = 0
        for text in filtered_text:
            w_cnt += len(text.split())
        print("FINAL FILTERED WORD AMOUNT:", w_cnt)    

        return filtered_text
    def run(self, keyword, text):
        '''
            Shortens the paragraph depending on the given keywords
            args:
                searching keywords
                paragraph
            return:
                shortened text
        '''
        running_cores = 8
        final_filtered_list = self._parallel_runner(text, keyword, running_cores)
        return final_filtered_list

if __name__ == "__main__":
    shortener = ParagraphShortener()

    paragraph = "İstanbul Türkiye'de yer alan şehir ve ülkenin 81 ilinden biri. Ülkenin en kalabalık, ekonomik,\
        tarihi ve sosyo-kültürel açıdan önde gelen şehridir.[6][7][8] Şehir, iktisadi büyüklük açısından dünyada 34.,\
        nüfus açısından belediye sınırları göz önüne alınarak yapılan sıralamaya göre Avrupa'da birinci, dünyada ise altıncı sırada\
        yer almaktadır.İstanbul Türkiye'nin kuzeybatısında, Marmara kıyısı ve Boğaziçi boyunca, Haliç'i de çevreleyecek şekilde\
        kurulmuştur. İstanbul kıtalararası bir şehir olup, Avrupa'daki bölümüne Avrupa Yakası veya Rumeli Yakası, Asya'daki\
        bölümüne ise Anadolu Yakası veya Asya Yakası denir. Tarihte ilk olarak üç tarafı Marmara Denizi, Boğaziçi ve Haliç'in\
        sardığı bir yarımada üzerinde kurulan İstanbul'un batıdaki sınırını İstanbul Surları oluşturmaktaydı. Gelişme ve büyüme\
        sürecinde surların her seferinde daha batıya ilerletilerek inşa edilmesiyle 4 defa genişletilen şehrin 39 ilçesi vardır.\
        Sınırları içerisinde ise büyükşehir belediyesi ile birlikte toplam 40 belediye bulunmaktadır. Dünyanın en eski şehirlerinden\
        biri olan İstanbul, 330-395 yılları arasında Roma İmparatorluğu, 395-1204 yılları arasında Bizans İmparatorluğu, 1204-1261\
        yılları arasında Latin İmparatorluğu, 1261-1453 yılları arasında tekrar Bizans İmparatorluğu ve son olarak 1453-1922 yılları\
        arasında Osmanlı İmparatorluğu'na başkentlik yaptı. Ayrıca İstanbul, Hilâfetin Osmanlı İmparatorluğu'na geçtiği 1517'den\
        kaldırıldığı 1924'e kadar İslam dünyasının da merkezi oldu. Son yıllarda birbiri ardına ortaya çıkartılan arkeolojik bulgularla\
        insanlık tarihine ilişkin önemli bilgiler elde edilmiştir. Yarımburgaz Mağarası'ndan çıkarılan taş aletlerle, ilkel insan\
        izlerinin 400.000 yıl öncesine dayandığı ortaya çıkmıştır. Anadolu Yakası'nda yürütülen kazı çalışmaları ve bunlara bağlı\
        araştırmalar, şehirde tarım ve hayvancılığa dayalı ilk yerleşik insan topluluğunun MÖ 5500'lere tarihlenen Fikirtepe\
        Kültürü olduğunu göstermiştir.Bu arkeolojik bulgular yalnızca İstanbul'un değil, tüm Marmara Bölgesi'nin en eski insan izleridir.\
        İstanbul sınırları içinde kent bazında ilk yerleşimler ise Anadolu Yakası'nda Kalkedon; Avrupa Yakası'nda Byzantion'dur.\
        Cumhuriyet dönemi öncesinde egemenliği altında olduğu devletlere yüzlerce yıl başkentlik yapan İstanbul, 13 Ekim 1923 tarihinde\
        başkentin Ankara'ya taşınmasıyla bu özelliğini yitirmiş; ancak ülkenin ticaret, sanayi, ulaşım, turizm, eğitim, kültür ve sanat\
        merkezi olma özelliğini sürdürmüştür."

    while True:
        keyword = input() 
        print(shortener.run(keyword, paragraph))
