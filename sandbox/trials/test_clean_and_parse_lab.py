from secdaily._02_xml.parsing.SecXmlLabParsing import SecLabXmlParser


def test_lab_xml_parsing():
    from secdaily._00_common.SecFileUtils import read_content_from_zip

    example_file = "D:/secprocessing2/xml/2025-03-15/0000055529-25-000013-kequ-20250131_lab.xml"
    content = read_content_from_zip(filename=example_file)

    lab_parser = SecLabXmlParser()
    df, errors = lab_parser.parse("0001078782-21-000058", content)

    print(df)
    print("\n")
    print(errors)



    # extractor = SecLabXmlExtractor()
    # extracted_data: SecLabLabelLink = extractor.extract("0001078782-21-000058", content)

    # transfomer = SecLabXmlTransformer()
    # transformed_data = transfomer.transform("0001078782-21-000058", extracted_data)

    # print(transformed_data)
