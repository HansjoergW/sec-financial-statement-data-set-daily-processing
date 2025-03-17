from secdaily._02_xml.parsing.lab._1_SecLabXmlExtracting import SecLabXmlExtractor, SecLabLabelLink
from secdaily._02_xml.parsing.lab._2_SecLabXmlTransformation import SecLabXmlTransformer


def test_lab_xml_parsing():
    from secdaily._00_common.SecFileUtils import read_content_from_zip

    example_file = "D:/secprocessing2/xml/2025-03-15/0000055529-25-000013-kequ-20250131_lab.xml"
    content = read_content_from_zip(filename=example_file)

    extractor = SecLabXmlExtractor()
    extracted_data: SecLabLabelLink = extractor.extract("0001078782-21-000058", content)

    transfomer = SecLabXmlTransformer()
    transformed_data = transfomer.transform("0001078782-21-000058", extracted_data)

    print(transformed_data)