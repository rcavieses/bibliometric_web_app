from datetime import datetime
import os
from typing import List, Dict, Any
from src.config.config_manager import PipelineConfig
from src.core.phase_runner import PhaseRunner, SearchPhase, AnalysisPhase, ReportPhase, DomainAnalysisPhase, ClassificationPhase, TableExportPhase  
from src.core.logger import Logger

class PipelineExecutor:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.logger = Logger()
        self._execution_completed = False
        
    def execute(self) -> bool:
        """Execute all pipeline phases according to configuration."""
        if not hasattr(self, '_execution_completed'):  # Primero verificar si existe
            self._execution_completed = False

        if self._execution_completed:
            print("Pipeline already executed. Create a new instance.")
            return False
        
        if not self.validate_config():
            self.logger.log_error("Invalid configuration")
            return False

        self.logger.start_pipeline()
        success = True

        try:
            phases = self._get_phases_to_run()
            total_phases = len(phases)
            
            for i, phase in enumerate(phases):
                phase_name = phase.get_description()
                self.logger.start_phase(phase_name)
                
                # Report phase start
                progress = i / total_phases
                self.report_progress(phase_name, progress, f"Starting {phase_name} phase...")
                
                # Execute the phase
                phase_success = phase.run()
                details = {"phase": phase_name}
                
                if not phase_success:
                    success = False
                    details["error"] = "Phase execution failed"
                    self.report_progress(phase_name, progress, f"Error in {phase_name} phase")
                    self.logger.end_phase(phase_success, details)
                    # Stop execution immediately after analysis phase failure
                    if "Analysis" in phase_name:
                        self.logger.log_error("Analysis phase failed - stopping pipeline")
                        break
                    break  # Stop for other phase failures too
                else:
                    # Report phase completion
                    progress = (i + 1) / total_phases
                    self.report_progress(phase_name, progress, f"Completed {phase_name} phase")
                
                self.logger.end_phase(phase_success, details)

        except Exception as e:
            self.logger.log_error(e)
            success = False
            self.report_progress("Error", 1.0, f"Error: {str(e)}")
        
        # Save execution summary
        stats = {
            "total_phases": len(phases),
            "completed": len([p for p in phases if p.run()]),
            "configuration": self._get_config_summary()
        }
        
        self.logger.end_pipeline(success, stats)
        self.logger.save_summary("pipeline_execution.json")
        self._execution_completed = True
        return success

    def validate_config(self) -> bool:
        """Validate pipeline configuration."""
        if not self.config:
            self.logger.log_error("No configuration provided")
            return False
            
        required_fields = ["domain1", "domain2", "figures_dir"]
        for field in required_fields:
            if not hasattr(self.config, field):
                self.logger.log_error(f"Missing required config field: {field}")
                return False
                
        # Validate input files exist
        if not os.path.exists(self.config.domain1):
            self.logger.log_error(f"Domain1 file not found: {self.config.domain1}")
            return False
            
        if not os.path.exists(self.config.domain2):
            self.logger.log_error(f"Domain2 file not found: {self.config.domain2}")
            return False
            
        return True

    def _get_phases_to_run(self) -> List[PhaseRunner]:
        """Determine which phases to run based on configuration."""
        phases = []
        executed_phases = set()
     
        # First check if we only want to generate the report
        if self.config.only_report:
            phases.append(ReportPhase(self.config))
            return phases
            
        # Then check if we only want analysis
        if self.config.only_analysis:
            phases.append(AnalysisPhase(self.config))
            if not self.config.skip_table:
                phases.append(TableExportPhase(self.config))
            return phases
        
        # If we get here, we either want search or all phases
        if not self.config.only_search:
            # Full pipeline
            all_phases = [
                SearchPhase(self.config),
                DomainAnalysisPhase(self.config),
                ClassificationPhase(self.config),
                AnalysisPhase(self.config),
                TableExportPhase(self.config),
                ReportPhase(self.config)
            ]
            
            # Filter out phases that should be skipped
            if self.config.skip_domain_analysis:
                all_phases = [p for p in all_phases if not isinstance(p, DomainAnalysisPhase)]
                all_phases = [p for p in all_phases if not isinstance(p, ClassificationPhase)]
                
            if self.config.skip_classification:
                all_phases = [p for p in all_phases if not isinstance(p, ClassificationPhase)]
                
            if self.config.skip_table:
                all_phases = [p for p in all_phases if not isinstance(p, TableExportPhase)]
                
            phases = all_phases
        else:
            # Only search phase
            phases = [SearchPhase(self.config)]
        
        return phases
    def get_results(self) -> Dict[str, Any]:
        """Get the results of the pipeline execution.
        
        Returns:
            Dict[str, Any]: Dictionary containing pipeline results and statistics
        """
        if not self._execution_completed:
            raise RuntimeError("Pipeline has not been executed yet.")
            
        return {
            "execution_completed": self._execution_completed,
            "configuration": self._get_config_summary(),
            "statistics": self.logger.get_statistics() if hasattr(self.logger, "get_statistics") else {},
            "phases_executed": [phase.get_description() for phase in self._get_phases_to_run()]
        }
    def _get_config_summary(self) -> Dict[str, Any]:
        """Create a summary of the current configuration."""
        return {
            "search_settings": {
                "max_results": self.config.max_results,
                "year_range": f"{self.config.year_start}-{self.config.year_end or 'present'}",
                "no_proxy": getattr(self.config, 'no_proxy', True)
            },
            "output_settings": {
                "figures_dir": self.config.figures_dir,
                "report_file": self.config.report_file
            },
            "flow_control": {
                "skip_searches": self.config.skip_searches,
                "skip_integration": self.config.skip_integration,
                "skip_domain_analysis": self.config.skip_domain_analysis,
                "skip_classification": self.config.skip_classification
            }
        }
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get a complete summary of the pipeline execution.
        
        Returns:
            Dict[str, Any]: Dictionary containing execution summary including configuration and statistics
        """
        if not self._execution_completed:
            raise RuntimeError("Pipeline has not been executed yet.")
            
        return {
            "execution_status": self._execution_completed,
            "configuration": self._get_config_summary(),
            "statistics": self.logger.get_statistics() if hasattr(self.logger, "get_statistics") else {},
            "phases": [phase.get_description() for phase in self._get_phases_to_run()],
            "execution_log": self.logger.get_summary() if hasattr(self.logger, "get_summary") else {}
        }

    def register_progress_callback(self, callback):
        """Register a callback for progress updates."""
        self.progress_callback = callback

    def report_progress(self, phase, progress, message):
        """Report progress to registered callback."""
        if hasattr(self, 'progress_callback') and self.progress_callback:
            self.progress_callback(phase, progress, message)