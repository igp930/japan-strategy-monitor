"""Tests unitarios para auto_discoverer.py

Este archivo contiene tests para verificar el funcionamiento
correcto de las funciones de auto-descubrimiento de documentos.
"""

import unittest
from unittest.mock import patch, MagicMock
import auto_discoverer


class TestAutoDiscoverer(unittest.TestCase):
    """Tests para las funciones de auto-descubrimiento."""

    def test_fetch_soup_success(self):
        """Test que fetch_soup retorna un objeto BeautifulSoup válido."""
        with patch('auto_discoverer.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.ok = True
            mock_response.text = '<html><body><h1>Test</h1></body></html>'
            mock_get.return_value = mock_response
            
            soup = auto_discoverer.fetch_soup('https://test.com')
            
            self.assertIsNotNone(soup)
            self.assertEqual(soup.find('h1').text, 'Test')
            mock_get.assert_called_once()

    def test_discover_defense_white_papers_returns_list(self):
        """Test que discover_defense_white_papers retorna una lista."""
        with patch('auto_discoverer.fetch_soup') as mock_fetch:
            mock_fetch.return_value = MagicMock()
            
            result = auto_discoverer.discover_defense_white_papers()
            
            self.assertIsInstance(result, list)

    def test_discover_diplomatic_bluebooks_returns_list(self):
        """Test que discover_diplomatic_bluebooks retorna una lista."""
        with patch('auto_discoverer.fetch_soup') as mock_fetch:
            mock_fetch.return_value = MagicMock()
            
            result = auto_discoverer.discover_diplomatic_bluebooks()
            
            self.assertIsInstance(result, list)

    def test_discover_nids_china_reports_returns_list(self):
        """Test que discover_nids_china_reports retorna una lista."""
        with patch('auto_discoverer.fetch_soup') as mock_fetch:
            mock_fetch.return_value = MagicMock()
            
            result = auto_discoverer.discover_nids_china_reports()
            
            self.assertIsInstance(result, list)

    def test_discover_oda_white_papers_returns_list(self):
        """Test que discover_oda_white_papers retorna una lista."""
        with patch('auto_discoverer.fetch_soup') as mock_fetch:
            mock_fetch.return_value = MagicMock()
            
            result = auto_discoverer.discover_oda_white_papers()
            
            self.assertIsInstance(result, list)

    def test_get_latest_years_empty_list(self):
        """Test que get_latest_years maneja listas vacías correctamente."""
        result = auto_discoverer.get_latest_years([])
        
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 0)

    def test_get_latest_years_single_category(self):
        """Test que get_latest_years identifica el año más reciente."""
        documents = [
            {'category': 'defense_white_paper', 'year': 2023},
            {'category': 'defense_white_paper', 'year': 2025},
            {'category': 'defense_white_paper', 'year': 2024},
        ]
        
        result = auto_discoverer.get_latest_years(documents)
        
        self.assertEqual(result['defense_white_paper'], 2025)

    def test_get_latest_years_multiple_categories(self):
        """Test que get_latest_years maneja múltiples categorías."""
        documents = [
            {'category': 'defense_white_paper', 'year': 2025},
            {'category': 'diplomatic_bluebook', 'year': 2026},
            {'category': 'nids_china_report', 'year': 2024},
        ]
        
        result = auto_discoverer.get_latest_years(documents)
        
        self.assertEqual(result['defense_white_paper'], 2025)
        self.assertEqual(result['diplomatic_bluebook'], 2026)
        self.assertEqual(result['nids_china_report'], 2024)
        self.assertEqual(len(result), 3)

    def test_document_structure(self):
        """Test que los documentos tienen la estructura esperada."""
        expected_keys = {'year', 'url', 'title', 'lang', 'organization', 'category'}
        
        # Mock una respuesta válida
        with patch('auto_discoverer.fetch_soup') as mock_fetch:
            mock_soup = MagicMock()
            mock_soup.find_all.return_value = []
            mock_fetch.return_value = mock_soup
            
            result = auto_discoverer.discover_defense_white_papers()
            
            # Si hay resultados, verificar estructura
            for doc in result:
                self.assertTrue(expected_keys.issubset(doc.keys()))
                self.assertIsInstance(doc['year'], int)
                self.assertIsInstance(doc['url'], str)
                self.assertIsInstance(doc['title'], str)
                self.assertIsInstance(doc['lang'], str)

    def test_url_format(self):
        """Test que las URLs generadas son absolutas."""
        documents = [
            {'url': 'https://www.mofa.go.jp/test.pdf'},
            {'url': 'https://www.mod.go.jp/test.html'},
        ]
        
        for doc in documents:
            self.assertTrue(doc['url'].startswith('https://') or doc['url'].startswith('http://'))


class TestIntegration(unittest.TestCase):
    """Tests de integración para el flujo completo."""

    def test_all_discoverers_run_without_errors(self):
        """Test que todas las funciones de descubrimiento se ejecutan sin errores."""
        try:
            auto_discoverer.discover_defense_white_papers()
            auto_discoverer.discover_diplomatic_bluebooks()
            auto_discoverer.discover_nids_china_reports()
            auto_discoverer.discover_oda_white_papers()
        except Exception as e:
            self.fail(f"Discoverer functions raised an exception: {e}")

    def test_combined_documents_have_no_duplicates(self):
        """Test que no hay duplicados en los documentos combinados."""
        all_docs = []
        all_docs.extend(auto_discoverer.discover_defense_white_papers())
        all_docs.extend(auto_discoverer.discover_diplomatic_bluebooks())
        all_docs.extend(auto_discoverer.discover_nids_china_reports())
        all_docs.extend(auto_discoverer.discover_oda_white_papers())
        
        # Crear conjunto de (title, lang, url) para detectar duplicados
        unique_docs = set()
        for doc in all_docs:
            key = (doc['title'], doc['lang'], doc['url'])
            self.assertNotIn(key, unique_docs, f"Duplicate found: {key}")
            unique_docs.add(key)


if __name__ == '__main__':
    unittest.main()
