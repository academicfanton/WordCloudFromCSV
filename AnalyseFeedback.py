from FeedbackPTLocals import LOCAL_PREFIX
from FeedbackPTLocals import LOCAL_LOOKUP
from FeedbackPTLocals import LOCAL_NONSTOP
import sys
import getopt
import string
import pandas as pd
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import spacy
from spacy.lang.pt.examples import sentences 
from spacy.lemmatizer import Lemmatizer

def left(s , amount):
    return s[:amount]

def show_wordcloud(data, sOutputFile='',bVerbose=False):
    wordcloud = WordCloud(
        background_color = 'white',
        max_words = 200,
        max_font_size = 40, 
        scale = 3,
        random_state = 42
    ).generate(str(data))

    fig = plt.figure(1, figsize = (20, 20))
    plt.axis('off')
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.show()
    if len(sOutputFile)>0:
        print("Writing output file: ",sOutputFile);
        plt.savefig(sOutputFile);
    
def clean_text(text,sLanguage,bVerbose=False):
    global LOCAL_LOOKUP;
    global LOCAL_PREFIX;
    global LOCAL_NONSTOP;
    if bVerbose:
        print(".. Original: ",text)
    # lower text
    text = text.lower()
    # Portuguese tokenizer
    nlp = spacy.load(sLanguage + '_core_news_sm')
    WordStr=""
    LemmaStr=""
    NLPtext = nlp(text)
    for word in NLPtext:
        if word.is_stop and (word.text not in LOCAL_NONSTOP):
            WordStr=word.text;
            if bVerbose:
                print(".... Ignore stop word: ",WordStr);
        elif not word.is_alpha:
            WordStr=word.text;
            if bVerbose:
                print(".... Ignore non alpha word: ",WordStr);
        else:
            CurrentLemma = word.lemma_.strip();
            CurrentWord = word.text.strip();
            if len(CurrentWord)<=1:
                CurrentWord=word.text;
                if bVerbose:
                   print(".... Ignore short word: ",CurrentWord);
            elif left(CurrentWord,3) in LOCAL_PREFIX:
                CurrentWord=word.text;
                if bVerbose:
                    print(".... Ignore absurd word: ",CurrentWord)
            else:
                if CurrentLemma in LOCAL_LOOKUP:
                    CurrentLemma=LOCAL_LOOKUP[CurrentLemma]
                if len(WordStr)>0:
                    WordStr = WordStr + ' '
                    LemmaStr = LemmaStr + ' '
                WordStr = (WordStr + CurrentWord).strip();
                LemmaStr = (LemmaStr + CurrentLemma).strip();
                if bVerbose:
                    print(".... ",CurrentWord, "converted to ",CurrentLemma)
    if bVerbose:
        print("-- ",LemmaStr)
    text=LemmaStr;
    return(text)


def ReadContent(sFile, sDelimiter=',',bVerbose=False):
    # read data
    ContentTxt = pd.read_csv(sFile,delimiter=sDelimiter,names=["REVIEWS"]);
    ContentTxt = ContentTxt.dropna();
    ContentTxt = ContentTxt.drop_duplicates();
    return ContentTxt;

# clean text data
def main():
    bVerbose=False;
    bSuccess=True;
    UsageString= '--- AnalyseFeedback.py ---\r\n';
    UsageString += '\t[-h] (Optional) Show this help message and exit\r\n';
    UsageString += '\t-i <Input csv file>\r\n';
    UsageString += '\t[-l] (Optional) <Language. Defaults to pt>\r\n';
    UsageString += '\t[-d] (Optional) <Delimiter. Defaults to ,>\r\n';
    UsageString += '\t[-o] (Optional) (NOT WORKING!) <Output graphic file (with extension)>\r\n';
    UsageString += '\t[-v] (Optional) Verbose output\r\n';
    sInputFile = '';
    sOutputFile = '';
    sLanguage='pt';
    sDelimiter=',';
	# Parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hi:o:vd:",["ifile=","ofile=","delimiter="]);
    except getopt.GetoptError:
        print(UsageString);
        print("");
        print('ERROR: Unable to process command line parameters');
        bSuccess=False;
    for opt, arg in opts:
        if opt == '-h':
            print(UsageString);
            sys.exit(1);
        elif opt == "-v":
            bVerbose = True;
        elif opt == "-l":
            sLanguage = arg;
        elif opt in ("-i", "--ifile"):
            sInputFile = arg;
        elif opt in ("-o", "--ofile"):
            sOutputFile = arg;
        elif opt in ("-d", "--delimiter"):
            sDelimiter = arg;
    if len(sInputFile)<=0:
        print(UsageString);
        print("");
        print('ERROR: Missing input file (-i / --ifile=)');
        bSuccess=False;

    if bSuccess:
        try:
            # read data
            print("Reading input file ",sInputFile);
            reviews_df = ReadContent(sInputFile,sDelimiter,bVerbose);
            print('%i lines to be processed' % len(reviews_df));
            print("Processing natural language (might take time) ..");
            reviews_df["review_clean"] = reviews_df["REVIEWS"].apply(lambda x: clean_text(x,sLanguage,bVerbose));
            print("Showing wordcloud ..");
            AllWords=" ".join(reviews_df["review_clean"]);
            show_wordcloud(AllWords,sOutputFile,bVerbose);
        except Exception as e:
            print("");
            print('ERROR: Error processing input');
            print(str(e));
            bSuccess=False;
    return bSuccess;


if __name__ == '__main__':
    bMainResult=main()
    if not bMainResult:
        exit(-1);
